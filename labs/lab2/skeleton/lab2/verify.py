"""The Lab 2 verifier: checks a test submission and scores it.

Copied into the task environment with task.json, checkpoints.json and, for
graded issue reproduction, solution.patch (see lab2.evaluate.stage_verifier),
then run as `python3 verify.py`. Paths come from the environment:

    CS408_TESTS  folder with this payload        (default /tests)
    CS408_OUT    output folder                   (default /logs/verifier)
    CS408_APP    the task repository             (default task.json workdir)

Steps:
 1. Submission: every file changed since the task's base commit (task.json
    "head") that is a test file in an allowed test directory and either does
    not exist at the base commit or is a starter test listed as editable is
    accepted and copied to $CS408_OUT/submission/ (cleared first). Any other
    change makes the submission invalid. With "collect_only" in task.json the
    verifier stops here (Harbor's in-run step; lab2.run then evaluates the
    submission in a fresh environment).
 2. Runs: before every run the repository is reset (tracked files to the base
    commit, untracked files removed) and the accepted files are copied back,
    so production code runs as supplied and no run sees another's leftovers.
    The tests run on the correct code (test writing, warmup); for issue
    reproduction on the unfixed code and, with solution.patch, on the
    repaired code. A run longer than CS408_TIMEOUT seconds (default 300) is
    killed and records "timeout"; all its tests count as absent.
 3. Score: a test is eligible if it passes on the correct (repaired) code and,
    for issue reproduction, fails or is absent on the unfixed code. Each
    faulty version (a patch applied to the correct/repaired code) is detected
    if an eligible test fails or is absent on it. A checkpoint's K is the
    fraction of its faulty versions detected; the score is 100 x mean K over
    the checkpoints that have faulty versions. Invalid submissions score 0.
    Faulty versions still waiting when the CS408_BUDGET seconds (default
    7200) for all faulty-version runs are used up are recorded with error
    "time budget" and are not detected.
    Issue reproduction without solution.patch reports the runs only.

Writes $CS408_OUT/eval.json (all details) and $CS408_OUT/reward.json
({"reward": score/100}, 0 without a score; collect-only: 1 if valid) for Harbor.

Python 3.9 compatible, standard library only (runs inside task images).
"""
import fnmatch
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath

SKILLS_DIR = ".skills"  # skill copies placed in the workdir for the agent; never part of a submission
TIMEOUT = 300  # seconds per test run (CS408_TIMEOUT overrides)
BUDGET = 7200  # seconds for all faulty-version runs together (CS408_BUDGET overrides)


def limit(name, default):
    return float(os.environ.get(name) or default)


def git(app, *args):
    return subprocess.run(["git", "-C", str(app)] + list(args), capture_output=True, text=True, check=True).stdout


def exists_at(app, commit, name):
    return subprocess.run(["git", "-C", str(app), "cat-file", "-e", commit + ":" + name],
                          capture_output=True).returncode == 0


def is_test_file(name, language):
    base = PurePosixPath(name).name
    if language == "go":
        return base.endswith("_test.go")
    return fnmatch.fnmatch(base, "test_*.py") or fnmatch.fnmatch(base, "*_test.py")


def accepted(name, spec, is_new):
    in_paths = any(PurePosixPath(name).is_relative_to(p) for p in spec["test_paths"])
    return in_paths and is_test_file(name, spec["language"]) and (is_new or name in spec["editable"])


# ------------------------------------------------------------------ test runs
def execute(cmd, cwd, env):
    """Run cmd in its own process group; on timeout kill the whole group and raise TimeoutExpired."""
    p = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                         start_new_session=True)
    try:
        out, err = p.communicate(timeout=limit("CS408_TIMEOUT", TIMEOUT))
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL)  # also ends test processes started by pytest or `go test`
        p.communicate()
        raise
    return p.returncode, out, err


def run_tests(app, spec, files):
    """Run the submitted test files once; returns {"tests": {id: passed|failed|skipped}, ...}."""
    check = spec.get("check") or {}
    strip = check.get("strip", "")
    args = [f[len(strip):] if strip and f.startswith(strip) else f for f in files]
    cwd = check.get("cwd", str(app))
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    try:
        if spec["language"] == "go":
            return run_go(cwd, args, check.get("go_args", ["-timeout", "120s"]), env)
        return run_pytest(cwd, args, check.get("pytest_args", []), env)
    except subprocess.TimeoutExpired:
        return {"exit_code": None, "timeout": True, "tests": {},
                "output_tail": "timeout: killed after {:g} s".format(limit("CS408_TIMEOUT", TIMEOUT))}


def run_pytest(cwd, files, pytest_args, env):
    """pytest with a JUnit XML report; test ids are <classname>.<name>."""
    with tempfile.TemporaryDirectory() as tmp:
        xml = os.path.join(tmp, "junit.xml")
        cmd = [sys.executable, "-m", "pytest"] + pytest_args + files + [
            "--junitxml=" + xml, "-p", "no:cacheprovider", "-q"]
        code, out, err = execute(cmd, cwd, env)
        tests = {}
        if os.path.exists(xml):
            for case in ET.parse(xml).iter("testcase"):
                status = "passed"
                for child in case:
                    if child.tag in ("failure", "error"):
                        status = "failed"
                    elif child.tag == "skipped" and status == "passed":
                        status = "skipped"
                tests[(case.get("classname") or "") + "." + (case.get("name") or "")] = status
    return {"exit_code": code, "tests": tests, "output_tail": (out + err)[-3000:]}


def run_go(cwd, files, go_args, env):
    """`go test -json` per package, restricted to the Test functions in the submitted files.

    A test that starts but never finishes (panic, timeout) or never runs
    (build failure) is recorded as failed.
    """
    packages = {}
    for f in files:
        names = re.findall(r"^func (Test\w+)\s*\(", (Path(cwd) / f).read_text(), re.M)
        packages.setdefault("./" + str(PurePosixPath(f).parent), set()).update(names)
    tests, output, code = {}, "", 0
    for pkg, names in sorted(packages.items()):
        if not names:
            continue
        cmd = ["go", "test", "-json", "-count=1"] + go_args + ["-run", "^(" + "|".join(sorted(names)) + ")$", pkg]
        returncode, stdout, stderr = execute(cmd, cwd, env)
        code = code or returncode
        started, finished, import_path = set(), set(), pkg
        for line in stdout.splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            import_path = event.get("Package") or import_path
            if not event.get("Test"):
                continue
            key = "{}.{}".format(event.get("Package", pkg), event["Test"])
            if event.get("Action") == "run":
                started.add(key)
            elif event.get("Action") in ("pass", "fail", "skip"):
                tests[key] = {"pass": "passed", "fail": "failed", "skip": "skipped"}[event["Action"]]
                finished.add(event["Test"].split("/")[0])
        for key in started - set(tests):
            tests[key] = "failed"
            finished.add(key.rsplit(".", 1)[-1].split("/")[0])
        for name in names - finished:
            tests["{}.{}".format(import_path, name)] = "failed"
        output += stdout[-1500:] + stderr[-1500:]
    return {"exit_code": code, "tests": tests, "output_tail": output[-3000:]}


def fails(run, test):
    """A test failed in a run; absent from the run (crash, collection error) counts as failed."""
    return run["tests"].get(test, "failed") == "failed"


class Repository:
    """The task repository at the base commit with the accepted test files on top."""

    def __init__(self, app, head, files, out, solution=None):
        self.app, self.head, self.files, self.out, self.solution = app, head, files, out, solution

    def reset(self, repaired=False):
        """Tracked files to the base commit (plus the repair), untracked files removed, accepted files back."""
        git(self.app, "reset", "-q", "--hard", self.head)
        git(self.app, "clean", "-fdq", "-e", SKILLS_DIR)
        if repaired:
            git(self.app, "apply", str(self.solution))
        for name in self.files:
            (self.app / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.out / "submission" / name, self.app / name)

    def run(self, spec, repaired=False, version=None):
        """One test run on a freshly reset tree, optionally with a faulty version applied."""
        self.reset(repaired)
        if version is not None:
            with tempfile.TemporaryDirectory() as tmp:
                patch = os.path.join(tmp, "faulty.patch")
                Path(patch).write_text(version["patch"])
                applied = subprocess.run(["git", "-C", str(self.app), "apply", patch], capture_output=True, text=True)
            if applied.returncode:
                return {"error": "patch does not apply: " + applied.stderr[-500:], "tests": {}}
        return run_tests(self.app, spec, self.files)


# ------------------------------------------------------------------ verifier
def submission(app, spec, out):
    """Classify changes since the base commit; copy accepted files to out/submission."""
    head = spec["head"]
    untracked = [n for n in git(app, "ls-files", "--others", "--exclude-standard", "-z").split("\0") if n]
    modified = [n for n in git(app, "diff", "--name-only", "-z", head).split("\0") if n]
    files, unexpected = [], []
    for name in sorted(set(untracked + modified)):
        if PurePosixPath(name).parts[0] == SKILLS_DIR:
            continue
        path = app / name
        # New means absent from the base commit, so staged (`git add`) new files count as new.
        if path.is_file() and not path.is_symlink() and accepted(name, spec, not exists_at(app, head, name)):
            files.append(name)
        else:
            unexpected.append(name)
    if git(app, "rev-parse", "HEAD").strip() != head:
        unexpected.append(".git/HEAD")
    for name in files:
        (out / "submission" / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(app / name, out / "submission" / name)
    return head, files, unexpected


def score(rows):
    """100 x mean K over the rows that have faulty versions (None if there are none)."""
    rows = [r for r in rows if r["K"] is not None]
    return round(100.0 * sum(r["K"] for r in rows) / len(rows), 4) if rows else None


def write(out, result, reward):
    """eval.json (all details) and reward.json for Harbor, which reads every key as a metric."""
    (out / "eval.json").write_text(json.dumps(result, indent=2) + "\n")
    (out / "reward.json").write_text(json.dumps({"reward": reward}) + "\n")
    print(json.dumps({k: result.get(k) for k in ("task", "valid_submission", "score", "public_score", "hidden_score")
                      if k in result}))
    return result


def verify(tests_dir, out, app=None):
    out.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(out / "submission", ignore_errors=True)  # only this run's accepted files end up here
    spec = json.loads((tests_dir / "task.json").read_text())
    catalog = json.loads((tests_dir / "checkpoints.json").read_text())["checkpoints"]
    solution = tests_dir / "solution.patch"
    app = Path(app or spec["workdir"])
    issue = spec["type"] == "issue-reproduction"
    scorable = not issue or solution.exists()

    head, files, unexpected = submission(app, spec, out)
    valid = bool(files) and not unexpected
    result = {"task": spec["id"], "type": spec["type"], "valid_submission": valid, "files": files,
              "unexpected_changes": unexpected}
    if spec.get("collect_only"):  # the reward of a collect-only run is 1 for a valid submission
        return write(out, dict(result, collect_only=True), float(valid))
    result.update({"reference_repair": issue and solution.exists(), "runs": {}, "eligible": [],
                   "checkpoints": [], "score": None})
    if files:
        repo = Repository(app, head, files, out, solution if solution.exists() else None)
        if issue:
            result["runs"]["unfixed"] = unfixed = repo.run(spec)
            if solution.exists():
                result["runs"]["repaired"] = reference = repo.run(spec, repaired=True)
                result["eligible"] = sorted(t for t, s in reference["tests"].items()
                                            if s == "passed" and fails(unfixed, t))
        else:
            result["runs"]["correct"] = reference = repo.run(spec)
            result["eligible"] = sorted(t for t, s in reference["tests"].items() if s == "passed")
        if scorable:
            deadline = time.monotonic() + limit("CS408_BUDGET", BUDGET)
            for checkpoint in catalog:
                versions = []
                for version in checkpoint["faulty_versions"]:
                    if not result["eligible"]:  # nothing can be detected; skip the run
                        run = {"tests": {}}
                    elif time.monotonic() > deadline:
                        run = {"error": "time budget", "tests": {}}
                    else:
                        run = repo.run(spec, repaired=issue, version=version)
                    # A faulty version that could not be applied or run is never detected.
                    detected = [] if run.get("error") else [t for t in result["eligible"] if fails(run, t)]
                    versions.append({"id": version["id"], "error": run.get("error"), "detected_by": detected})
                result["checkpoints"].append({
                    "id": checkpoint["id"], "label": checkpoint.get("label"), "hidden": bool(checkpoint.get("hidden")),
                    "K": sum(bool(v["detected_by"]) for v in versions) / len(versions) if versions else None,
                    "faulty_versions": versions})
        repo.reset()  # leave the submission on the base code
    elif scorable:
        result["checkpoints"] = [{"id": c["id"], "label": c.get("label"), "hidden": bool(c.get("hidden")),
                                  "K": 0.0 if c["faulty_versions"] else None, "faulty_versions": []} for c in catalog]

    if scorable:
        rows = result["checkpoints"]
        result["score"] = score(rows) if valid else (0.0 if score(rows) is not None else None)
        if any(r["hidden"] for r in rows):
            for part, hidden in (("public", False), ("hidden", True)):
                part_score = score([r for r in rows if r["hidden"] == hidden])
                result[part + "_score"] = part_score if valid or part_score is None else 0.0
    return write(out, result, (result["score"] or 0.0) / 100.0)


def main():
    verify(Path(os.environ.get("CS408_TESTS", "/tests")), Path(os.environ.get("CS408_OUT", "/logs/verifier")),
           os.environ.get("CS408_APP"))


if __name__ == "__main__":
    main()
