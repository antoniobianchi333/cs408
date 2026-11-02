"""Command line validation, task registry, jobs layout and submit."""
import json
import shutil

import pytest
import yaml

from conftest import write_task
from lab2 import jobs, tasks
from lab2.__main__ import main


def cli(capsys, *args):
    code = main(list(args))
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_task_registry(lab):
    task = tasks.load("calc")
    assert (task.type, task.dir, task.workdir) == ("warmup", lab / "tasks/warmup/calc", "/app")
    assert task.prompt().endswith("Allowed test directories: .\n")
    with pytest.raises(ValueError, match="unknown task 'nope'"):
        tasks.load("nope")
    spec = yaml.safe_load((task.dir / "task.yaml").read_text())
    (task.dir / "task.yaml").write_text(yaml.safe_dump(spec | {"type": "test-writing"}))
    with pytest.raises(ValueError, match="must match the folder"):
        tasks.all_tasks()


@pytest.mark.parametrize("alias", ["-x", "a b", "", "a/b", "submission", "vanilla", "Vanilla", "SUBMISSION"])
def test_run_rejects_invalid_and_reserved_aliases(lab, capsys, alias):
    code, _, err = cli(capsys, "run", f"--alias={alias}", "--tasks", "calc")
    assert code == 2 and ("reserved" in err if alias.isalpha() else "invalid alias" in err)


@pytest.mark.parametrize("alias", ["vanilla", "VANILLA"])
def test_eval_refuses_vanilla(lab, capsys, alias):
    (lab / "jobs" / alias / "calc").mkdir(parents=True)
    code, _, err = cli(capsys, "eval", "--alias", alias, "--tasks", "calc")
    assert code == 2 and "read-only" in err


def test_eval_checks_checkpoint_files(lab, capsys):
    (lab / "jobs/A/calc").mkdir(parents=True)
    code, _, err = cli(capsys, "eval", "--alias", "A", "--tasks", "calc", "--checkpoints", str(lab / "missing.json"))
    assert code == 2 and "does not exist" in err
    (lab / "bad.json").write_text(json.dumps({"task": "calc", "checkpoints": [{"id": "x"}]}))
    code, _, err = cli(capsys, "eval", "--alias", "A", "--tasks", "calc", "--checkpoints", str(lab / "bad.json"))
    assert code == 2 and "'faulty_versions'" in err


def test_job_layout(lab):
    task = tasks.load("calc")
    assert jobs.job_dir("A.b_c-1", task) == lab / "jobs/A.b_c-1/calc"
    assert jobs.job_dir("submission", task) == lab / "jobs/submission/warmup/calc"
    assert jobs.check_alias("vanilla", writable=False) == "vanilla"


def test_run_validates_everything_before_running(lab, capsys, monkeypatch):
    import lab2.run

    monkeypatch.setattr(lab2.run, "run_task", lambda *a: pytest.fail("must not run"))
    (lab / "jobs/A/calc").mkdir(parents=True)
    assert "pass --redo-existing" in cli(capsys, "run", "--alias", "A", "--tasks", "calc")[2]
    assert "unknown task" in cli(capsys, "run", "--alias", "B", "--tasks", "calc", "nope")[2]
    assert "no such skill" in cli(capsys, "run", "--alias", "B", "--tasks", "calc", "--skills", "missing")[2]


def test_redo_existing_replaces_the_job(lab, capsys, monkeypatch):
    import lab2.model
    import lab2.run

    calls = []
    monkeypatch.setattr(lab2.model, "hide_process_environment", lambda: None)  # keep the test process as it is
    monkeypatch.setattr(lab2.run, "run_task", lambda alias, task, selected, config, redo, command:
                        calls.append((task.id, redo, command)) or
                        {"task": task.id, "exit_status": "Submitted", "valid_submission": True, "score": 1.0,
                         "errors": ["first line\nmore"]})
    (lab / "jobs/A/calc").mkdir(parents=True)
    code, out, _ = cli(capsys, "run", "--alias", "A", "--tasks", "calc", "--redo-existing")
    # exit status 1: the (fake) task ended with an error
    assert code == 1 and calls == [("calc", True, "python -m lab2 run --alias A --tasks calc --redo-existing")]
    assert "  error: first line\n" in out and "more" not in out


def test_submit(lab, capsys):
    write_task(lab, "second")
    (lab / "jobs/A/calc/submission").mkdir(parents=True)
    (lab / "jobs/A/calc/skills/probe").mkdir(parents=True)
    (lab / "jobs/A/calc/skills/probe/SKILL.md").write_text("v1")
    skills = [{"name": "probe", "description": "d", "path": "skills/probe"}]
    (lab / "jobs/A/calc/run.json").write_text(json.dumps({"skills": skills}))
    code, _, err = cli(capsys, "submit", "--alias", "A", "--type", "warmup")
    assert code == 2 and "no job for second" in err
    (lab / "jobs/A/second").mkdir(parents=True)
    code, _, err = cli(capsys, "submit", "--alias", "A", "--type", "warmup")  # second ran without skills
    assert code == 2 and "same skills (calc: probe; second: no skills)" in err
    shutil.copytree(lab / "jobs/A/calc/skills", lab / "jobs/A/second/skills")
    (lab / "jobs/A/second/skills/probe/SKILL.md").write_text("v2")  # same name, different content
    assert "same skills" in cli(capsys, "submit", "--alias", "A", "--type", "warmup")[2]
    (lab / "jobs/A/second/skills/probe/SKILL.md").write_text("v1")
    assert cli(capsys, "submit", "--alias", "A", "--type", "warmup")[0] == 0
    record = json.loads((lab / "jobs/submission/warmup/submission.json").read_text())
    assert record["alias"] == "A" and record["tasks"] == ["calc", "second"]
    assert record["skills"] == skills and record["submitted_at"]
    assert (lab / "jobs/submission/warmup/calc/submission").is_dir()
    code, _, err = cli(capsys, "submit", "--alias", "A", "--type", "warmup")
    assert code == 2 and "--resubmit-existing" in err
    (lab / "jobs/A/calc/new.txt").write_text("x")
    assert cli(capsys, "submit", "--alias", "A", "--type", "warmup", "--resubmit-existing")[0] == 0
    assert (lab / "jobs/submission/warmup/calc/new.txt").exists()
    assert "reserved" in cli(capsys, "submit", "--alias", "submission", "--type", "warmup")[2]


def test_eval_needs_existing_jobs(lab, capsys):
    code, _, err = cli(capsys, "eval", "--alias", "A", "--tasks", "calc")
    assert code == 2 and "no job for calc" in err


def test_tasks_listing(lab, capsys):
    code, out, _ = cli(capsys, "tasks")
    assert code == 0 and out.split() == ["calc", "warmup", "python", "local"]
