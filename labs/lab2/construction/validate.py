"""Validate the task images: /app state and the official checks of each source task.

    python construction/validate.py [TASK ...] [--store DIR]

The image (task.yaml environment.image) is taken from the udocker store given
with --store, else as lab2 finds it (the shared copy, or pulled). For each task, one
container is created, checked and removed:
  * /app: HEAD = task.yaml environment.head, tree = the build recipe's app_tree,
    clean working tree;
  * SWE-Atlas TW: the shipped tests pass ("correct"), the reference tests
    (reference-tests/, the Atlas reference test file) pass ("reference") and the Atlas skeleton swap
    (source/skeleton_code_swap.patch) makes reference tests fail ("skeleton");
  * DeepSWE IR: with the official tests (source/test.patch), `test.sh base|new` on the
    unfixed and on the repaired code (the task's solution.patch): every P2P test passes
    on both, every F2P test fails on the unfixed and passes on the repaired code
    (source/config.json).
It prints one line per task (OK or FAILED, passed/total tests per run) and the
problems found; the exit status is 1 if any task failed. Known environment
failures are listed in KNOWN_FAILURES (udocker runs as root).
"""
import argparse
import json
import shutil
import subprocess
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path

from images.build import RECIPES, data_dir, task_ids, tasks
from lab2.environments import Udocker

KNOWN_FAILURES = {"paperless": ["documents.tests.test_file_handling.TestFileHandling.test_file_renaming_missing_permissions"]}
# Test command of the Atlas reference tests ({xml}: junit report path inside the container).
ATLAS_TESTS = {
    "paperless": "cd /app/src && pytest --override-ini=addopts= -p no:sugar -p no:cacheprovider --no-cov -n 1"
                 " --junitxml={xml} documents/tests/test_file_handling.py",
    "minio": "go test -json -count=1 -timeout 300s ./internal/etag",
    "k6": "go test -json -count=1 -timeout 300s ./lib",
}
W = "/tmp/lab2-validate"  # scratch folder inside the container


class Container:
    """One container of the task image; runs shell commands in /app."""

    def __init__(self, udocker, task):
        self.udocker, self.task = udocker, task
        self.name = "lab2-validate-" + uuid.uuid4().hex[:8]
        udocker.ensure_image(task.spec["environment"]["image"])  # without --store: the shared copy
        self.root = udocker.create(self.name, task.spec["environment"]["image"])
        (self.root / W.lstrip("/")).mkdir(parents=True)

    def put(self, path):
        shutil.copyfile(path, self.root / W.lstrip("/") / Path(path).name)

    def sh(self, command, env=None, check=False):
        args = self.udocker.run_args(self.name, "/app", {**self.task.env, **(env or {})})
        p = subprocess.run(args + ["bash", "-c", command], env=self.udocker.env, capture_output=True, text=True, timeout=3600)
        if check and p.returncode:
            raise RuntimeError(f"{command}: rc {p.returncode}\n{(p.stdout + p.stderr)[-2000:]}")
        return p

    def tests(self, command, env=None):
        """Run a test command; results from the junit report ({xml}) or the `go test -json` output."""
        xml = f"{W}/report.xml"
        host_xml = self.root / xml.lstrip("/")
        host_xml.unlink(missing_ok=True)
        p = self.sh(command.replace("{xml}", xml), env)
        tests = {}
        if host_xml.exists():
            for case in ET.parse(host_xml).iter("testcase"):
                tags = {child.tag for child in case}
                status = "failed" if tags & {"failure", "error"} else "skipped" if "skipped" in tags else "passed"
                tests[case.get("classname") + "." + case.get("name")] = status
        for line in p.stdout.splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if isinstance(event, dict) and event.get("Test") and event.get("Action") in ("pass", "fail", "skip"):
                status = {"pass": "passed", "fail": "failed", "skip": "skipped"}[event["Action"]]
                tests[event["Package"] + "." + event["Test"]] = status
        counts = {s: sum(v == s for v in tests.values()) for s in ("passed", "failed", "skipped")}
        return {"rc": p.returncode, "counts": counts, "tests": dict(sorted(tests.items()))}

    def remove(self):
        self.udocker.remove(self.name)


def check_app(c, task):
    head = c.sh("git rev-parse HEAD", check=True).stdout.strip()
    tree = c.sh("git rev-parse 'HEAD^{tree}'", check=True).stdout.strip()
    dirty = c.sh("git status --porcelain", check=True).stdout.strip()
    expected = (task.spec["environment"]["head"], RECIPES[task.id]["app_tree"], "")
    return [] if (head, tree, dirty) == expected else [f"/app is HEAD {head} tree {tree} dirty={bool(dirty)}, expected {expected[:2]}"]


def atlas(c, task, records):
    known = set(KNOWN_FAILURES.get(task.id, []))
    c.put(data_dir(task) / "source/skeleton_code_swap.patch")
    command, problems = ATLAS_TESTS[task.id], []
    records["correct"] = c.tests(command)
    shutil.copytree(data_dir(task) / "reference-tests", c.root / "app", dirs_exist_ok=True)
    records["reference"] = c.tests(command)
    c.sh(f"git apply {W}/skeleton_code_swap.patch", check=True)
    records["skeleton"] = c.tests(command)
    for phase in ("correct", "reference"):
        failed = [t for t, s in records[phase]["tests"].items() if s == "failed" and t not in known]
        if failed or not records[phase]["tests"]:
            problems.append(f"{phase}: failing {failed[:5]} of {len(records[phase]['tests'])}")
    passed = {t for t, s in records["reference"]["tests"].items() if s == "passed"}
    if not any(records["skeleton"]["tests"].get(t, "failed") != "passed" for t in passed):
        problems.append("skeleton: no reference test fails on the skeleton code")
    return problems


def deepswe(c, task, records):
    source = data_dir(task) / "source"
    config = json.loads((source / "config.json").read_text())
    f2p, p2p = set(config["f2p_node_ids"]), set(config["p2p_node_ids"])
    c.put(source / "test.patch")
    c.put(task.solution)
    c.sh(f"git apply {W}/test.patch", check=True)
    # Machine-readable results: go test JSON events, pytest JUnit XML.
    if task.spec["language"] == "go":
        env = {"GOFLAGS": "-p=4 -json"}
    else:
        env = {"PYTEST_ADDOPTS": "-p no:cacheprovider --junitxml={xml}"}
    problems = []
    for phase in ("unfixed", "repaired"):
        if phase == "repaired":
            c.sh(f"git apply {W}/solution.patch", check=True)
        results = {}
        for suite in ("base", "new"):
            run_env = {k: v.replace("{xml}", f"{W}/report.xml") for k, v in env.items()}
            records[f"{phase}-{suite}"] = run = c.tests(f"bash test.sh {suite}", run_env)
            results.update(run["tests"])
        passed = {t for t, s in results.items() if s == "passed"}
        bad_p2p = sorted(p2p - passed)
        bad_f2p = sorted(f2p & passed) if phase == "unfixed" else sorted(f2p - passed)
        if bad_p2p or bad_f2p:
            problems.append(f"{phase}: P2P not passing {bad_p2p[:5]} ({len(bad_p2p)}); F2P wrong {bad_f2p[:5]} ({len(bad_f2p)})")
    return problems


def validate(task, udocker):
    c = Container(udocker, task)
    records = {}
    try:
        problems = check_app(c, task)
        problems += atlas(c, task, records) if task.spec["source"]["dataset"] == "SWE-Atlas TW" else deepswe(c, task, records)
    finally:
        c.remove()
    summary = ", ".join(f"{p} {r['counts']['passed']}/{len(r['tests'])} passed" for p, r in records.items())
    print(f"{task.id}: {'OK' if not problems else 'FAILED'} ({summary})")
    for p in problems:
        print(f"  {p}")
    return not problems


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("tasks", nargs="*", help="task ids (default: all six image tasks)")
    parser.add_argument("--store", type=Path, help="udocker image store (default: the lab2 store)")
    args = parser.parse_args()
    udocker = Udocker(args.store)
    ok = True
    for task_id in task_ids(args.tasks):
        ok = validate(tasks.load(task_id), udocker) and ok
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
