"""evaluate_job on saved jobs of a made-up local task."""
import json

import pytest
import yaml

from conftest import STARTER
from lab2 import tasks
from lab2.evaluate import evaluate_job
from test_verify import GOOD


def save_job(folder, files, run=None):
    for name, text in files.items():
        (folder / "submission" / name).parent.mkdir(parents=True, exist_ok=True)
        (folder / "submission" / name).write_text(text)
    if run:
        (folder / "run.json").write_text(json.dumps(run))
    return folder


def test_evaluate_job_writes_the_named_file(lab):
    task = tasks.load("calc")
    job = save_job(lab / "jobs/A/calc", {"test_new.py": GOOD}, {"alias": "A", "skills": [], "exit_status": "Submitted",
                                                                 "errors": []})
    result = evaluate_job(job, "calc", [task.checkpoints])
    assert result == json.loads((job / "eval.json").read_text()) and result["score"] == 100.0
    assert result["job"] == {"alias": "A", "skills": [], "exit_status": "Submitted", "errors": []}
    evaluate_job(job, "calc", [task.checkpoints], out_name="eval-full.json")
    assert (job / "eval-full.json").exists()
    with pytest.raises(ValueError, match="no job"):
        evaluate_job(lab / "jobs/A/missing", "calc", [task.checkpoints])


def test_extra_editable_accepts_edited_starter_tests(lab):
    task = tasks.load("calc")
    spec = yaml.safe_load((task.dir / "task.yaml").read_text())
    (task.dir / "task.yaml").write_text(yaml.safe_dump(spec | {"editable": []}))
    job = save_job(lab / "jobs/A/calc", {"test_calc.py": STARTER + "\n" + GOOD.split("\n", 1)[1]})
    assert evaluate_job(job, "calc", [task.checkpoints])["unexpected_changes"] == ["test_calc.py"]
    assert evaluate_job(job, "calc", [task.checkpoints], extra_editable=["test_calc.py"])["valid_submission"]
