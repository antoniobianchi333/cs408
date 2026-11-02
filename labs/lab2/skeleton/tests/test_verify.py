"""verify.py rules on a small git repository (the `calc` fixture task)."""
import json
import subprocess
import tempfile
from pathlib import Path

import pytest

from conftest import CALC, STARTER, patch, write_task
from lab2 import tasks
from lab2.environments import create_workspace
from lab2.evaluate import merge_checkpoints, stage_verifier
from lab2.verify import verify

GOOD = "from calc import double, sign\n\n\ndef test_double():\n    assert double(3) == 6\n\n\n" \
       "def test_sign():\n    assert sign(0) == 1 and sign(-2) == -1\n"
WEAK = "from calc import double\n\n\ndef test_double():\n    assert double(3) == 6\n"


def evaluate(lab, files, task_id="calc", solution=None, checkpoints=None, edit=None, collect_only=False):
    """Stage the verifier, write `files` into a fresh workspace, run verify; returns eval.json."""
    task, scratch = tasks.load(task_id), Path(tempfile.mkdtemp(dir=lab))
    tests = stage_verifier(task, scratch / "payload", checkpoints or [task.checkpoints], solution,
                           collect_only=collect_only)
    root = create_workspace(task.dir / "project", scratch / "workspace")
    for name, text in files.items():
        (root / "app" / name).parent.mkdir(parents=True, exist_ok=True)
        (root / "app" / name).write_text(text)
    if edit:
        edit(root / "app")
    result = verify(tests, scratch / "out", root / "app")
    assert json.loads((scratch / "out/eval.json").read_text()) == result
    reward = float(result["valid_submission"]) if collect_only else (result["score"] or 0) / 100
    assert json.loads((scratch / "out/reward.json").read_text()) == {"reward": reward}
    result["out"], result["app"] = scratch / "out", root / "app"
    return result


def test_scoring_with_hidden_checkpoints(lab):
    result = evaluate(lab, {"test_new.py": GOOD})
    assert result["valid_submission"] and result["files"] == ["test_new.py"]
    assert {c["id"]: c["K"] for c in result["checkpoints"]} == {"double": 1.0, "sign": 1.0}
    assert result["score"] == 100.0 and result["public_score"] == 100.0 and result["hidden_score"] == 100.0
    assert (result["out"] / "submission/test_new.py").read_text() == GOOD


def test_partial_detection_and_failing_tests_are_not_eligible(lab):
    failing = WEAK + "\n\ndef test_wrong():\n    assert double(1) == 3\n"
    result = evaluate(lab, {"test_new.py": failing})
    assert result["eligible"] == ["test_new.test_double"]
    assert {c["id"]: c["K"] for c in result["checkpoints"]} == {"double": 1.0, "sign": 0.0}
    assert result["score"] == 50.0 and result["hidden_score"] == 0.0


def test_editable_starter_and_skills_folder(lab):
    result = evaluate(lab, {"test_calc.py": STARTER + "\n" + GOOD.split("\n", 1)[1], ".skills/x/SKILL.md": "x"})
    assert result["valid_submission"] and result["files"] == ["test_calc.py"]


@pytest.mark.parametrize("files,unexpected", [
    ({"test_new.py": GOOD, "calc.py": CALC.replace("2 * x", "x + x")}, ["calc.py"]),
    ({"test_new.py": GOOD, "notes.txt": "x"}, ["notes.txt"]),
    ({"test_new.py": GOOD, "helper.py": "X = 1\n"}, ["helper.py"])])
def test_changes_outside_tests_make_the_submission_invalid(lab, files, unexpected):
    result = evaluate(lab, files)
    assert not result["valid_submission"] and result["unexpected_changes"] == unexpected
    assert result["score"] == 0.0 and result["checkpoints"]  # tests still run, on the restored code
    assert result["runs"]["correct"]["tests"]["test_new.test_double"] == "passed"


def test_commits_and_empty_submissions(lab):
    def commit(app):
        subprocess.run(["git", "-C", str(app), "add", "."], check=True)
        subprocess.run(["git", "-C", str(app), "-c", "user.name=x", "-c", "user.email=x@x", "commit", "-qm", "x"],
                       check=True)

    committed = evaluate(lab, {"test_new.py": GOOD}, edit=commit)
    assert ".git/HEAD" in committed["unexpected_changes"] and committed["score"] == 0.0
    empty = evaluate(lab, {})
    assert not empty["valid_submission"] and empty["score"] == 0.0 and not empty["runs"]


def test_staged_new_test_file_is_accepted(lab):
    result = evaluate(lab, {"test_new.py": GOOD}, edit=lambda app: subprocess.run(
        ["git", "-C", str(app), "add", "test_new.py"], check=True))
    assert result["valid_submission"] and result["files"] == ["test_new.py"] and result["score"] == 100.0


def test_collect_only_copies_the_submission_without_runs(lab):
    result = evaluate(lab, {"test_new.py": GOOD}, collect_only=True)
    assert result == {"task": "calc", "type": "warmup", "valid_submission": True, "files": ["test_new.py"],
                      "unexpected_changes": [], "collect_only": True, "out": result["out"], "app": result["app"]}
    assert (result["out"] / "submission/test_new.py").read_text() == GOOD


def test_output_submission_folder_is_cleared(lab, tmp_path):
    task = tasks.load("calc")
    tests = stage_verifier(task, tmp_path / "payload", [task.checkpoints])
    app = create_workspace(task.dir / "project", tmp_path / "workspace") / "app"
    (app / "test_new.py").write_text(GOOD)
    (tmp_path / "out/submission").mkdir(parents=True)
    (tmp_path / "out/submission/calc.py").write_text("planted\n")
    verify(tests, tmp_path / "out", app)
    assert sorted(p.name for p in (tmp_path / "out/submission").iterdir()) == ["test_new.py"]


def test_every_run_starts_from_a_reset_tree(lab):
    """A test that overwrites production code and leaves files behind affects only its own run."""
    clobber = GOOD + "\n\ndef test_zz_clobber():\n    open('calc.py', 'w').write('X = 1\\n')\n" \
                     "    open('leftover.txt', 'w').write('x')\n"
    result = evaluate(lab, {"test_new.py": clobber})
    assert all(v["error"] is None for c in result["checkpoints"] for v in c["faulty_versions"])
    assert {c["id"]: c["K"] for c in result["checkpoints"]} == {"double": 1.0, "sign": 1.0}
    assert (result["app"] / "calc.py").read_text() == CALC and not (result["app"] / "leftover.txt").exists()


HANGS_IF_WRONG = "from calc import double\n\n\ndef test_double():\n    while double(3) != 6:\n        pass\n"


def test_timeouts_count_as_absent_tests(lab, monkeypatch):
    monkeypatch.setenv("CS408_TIMEOUT", "3")
    result = evaluate(lab, {"test_new.py": HANGS_IF_WRONG})
    double, sign = result["checkpoints"]
    # The faulty version makes the test loop forever: the killed run counts as detection.
    assert double["K"] == 1.0 and double["faulty_versions"][0]["detected_by"] == ["test_new.test_double"]
    assert sign["K"] == 0.0
    slow = evaluate(lab, {"test_new.py": "import time\n\n\ndef test_slow():\n    time.sleep(60)\n"})
    assert slow["runs"]["correct"]["timeout"] and slow["runs"]["correct"]["tests"] == {}
    assert slow["eligible"] == [] and slow["score"] == 0.0


def test_time_budget_stops_faulty_version_runs(lab, monkeypatch):
    monkeypatch.setenv("CS408_BUDGET", "0")
    result = evaluate(lab, {"test_new.py": GOOD})
    assert [v["error"] for c in result["checkpoints"] for v in c["faulty_versions"]] == ["time budget"] * 3
    assert result["score"] == 0.0


def test_faulty_version_that_does_not_apply_is_not_detected(lab):
    data = json.loads((lab / "tasks/warmup/calc/checkpoints.json").read_text())
    data["checkpoints"][0]["faulty_versions"][0]["patch"] = patch("calc.py", "other\n", "changed\n")
    (lab / "broken.json").write_text(json.dumps(data))
    result = evaluate(lab, {"test_new.py": GOOD}, checkpoints=[lab / "broken.json"])
    version = result["checkpoints"][0]["faulty_versions"][0]
    assert version["error"].startswith("patch does not apply") and version["detected_by"] == []


def test_checkpoint_files_are_concatenated_with_unique_ids(lab):
    task = tasks.load("calc")
    data = json.loads(task.checkpoints.read_text())
    (lab / "a.json").write_text(json.dumps({"task": "calc", "checkpoints": data["checkpoints"][:1]}))
    (lab / "b.json").write_text(json.dumps({"task": "calc", "checkpoints": data["checkpoints"][1:]}))
    assert [c["id"] for c in merge_checkpoints(task, [lab / "a.json", lab / "b.json"])["checkpoints"]] == \
        ["double", "sign"]
    with pytest.raises(ValueError, match="duplicate checkpoint ids: double"):
        merge_checkpoints(task, [lab / "a.json", lab / "a.json"])
    (lab / "c.json").write_text(json.dumps({"task": "other", "checkpoints": []}))
    with pytest.raises(ValueError, match="not 'calc'"):
        merge_checkpoints(task, [lab / "c.json"])


@pytest.fixture
def issue(lab):
    """Issue reproduction: the project has a bug in sign(0); solution.patch repairs it.

    Faulty versions are relative to the repaired code.
    """
    buggy = CALC.replace("x < 0", "x <= 0")
    folder = write_task(lab, "bug", "issue-reproduction", calc=buggy, editable=[])
    data = json.loads((folder / "checkpoints.json").read_text())
    data["checkpoints"] = [{"id": "zero", "label": "sign(0) is 1", "hidden": False, "faulty_versions": [
        {"id": "zero-negative", "patch": patch("calc.py", CALC, CALC.replace("return 1\n", "return -1 if x == 0 else 1\n"))}]}]
    (folder / "checkpoints.json").write_text(json.dumps(data))
    (lab / "solution.patch").write_text(patch("calc.py", buggy, CALC))
    return lab / "solution.patch"


REPRO = "from calc import sign\n\n\ndef test_zero():\n    assert sign(0) == 1\n\n\n" \
        "def test_negative():\n    assert sign(-1) == -1\n"


def test_issue_reproduction_with_repair(issue, lab):
    result = evaluate(lab, {"test_bug.py": REPRO}, "bug", solution=issue)
    assert result["reference_repair"] and result["runs"]["unfixed"]["tests"]["test_bug.test_zero"] == "failed"
    assert result["eligible"] == ["test_bug.test_zero"]  # test_negative passes on the unfixed code too
    assert result["score"] == 100.0


def test_issue_reproduction_missing_on_unfixed_counts_as_failing(issue, lab):
    crashing = "import calc\nif calc.sign(0) != 1:\n    raise ImportError('unfixed')\n\n\n" + REPRO
    result = evaluate(lab, {"test_bug.py": crashing}, "bug", solution=issue)
    assert "test_bug.test_zero" not in result["runs"]["unfixed"]["tests"]
    assert set(result["eligible"]) == {"test_bug.test_zero", "test_bug.test_negative"}


def test_issue_reproduction_without_repair_reports_runs_only(issue, lab):
    result = evaluate(lab, {"test_bug.py": REPRO}, "bug")
    assert not result["reference_repair"] and result["score"] is None and result["checkpoints"] == []
    assert set(result["runs"]) == {"unfixed"}
    assert json.loads((result["out"] / "reward.json").read_text()) == {"reward": 0.0}
