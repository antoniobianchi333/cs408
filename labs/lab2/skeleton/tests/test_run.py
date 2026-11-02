"""Harbor export, the record of a failed run, and one end-to-end Harbor run of a made-up local task.

The run uses the fake model endpoint; no test calls the Purdue API.
"""
import json
import tempfile
import tomllib

import yaml

from conftest import command, write_skill, write_task
from lab2 import tasks
from lab2.run import CONFIG, export, run


def test_export_image_task(lab, tmp_path):
    folder = write_task(lab, "img", "test-writing", prepare="true", environment={
        "image": "cs408-lab2/img:arm64", "archive": "img-arm64.tar.gz", "workdir": "/app",
        "head": "abc", "env": {"A": 1}})
    (folder / "project").rename(folder / "unused")
    task = tasks.load("img")
    dest = export(task, tmp_path / "harbor/img", yaml.safe_load(CONFIG.read_text()))
    config = tomllib.loads((dest / "task.toml").read_text())
    assert config["environment"]["docker_image"] == "cs408-lab2/img:arm64"
    assert config["environment"]["env"] == {"A": "1"} and config["environment"]["workdir"] == "/app"
    assert config["environment"]["healthcheck"]["command"] == "cd /app && true"
    assert (dest / "instruction.md").read_text() == task.prompt()
    assert sorted(p.name for p in (dest / "tests").iterdir()) == ["checkpoints.json", "task.json", "test.sh", "verify.py"]
    info = json.loads((dest / "tests/task.json").read_text())
    assert info["head"] == "abc" and info["collect_only"]  # Harbor only collects; lab2.run evaluates
    assert json.loads((dest / "tests/checkpoints.json").read_text())["checkpoints"] == []


def test_failed_harbor_run_is_recorded_and_other_tasks_continue(lab, monkeypatch, tmp_path):
    import lab2.run

    write_task(lab, "second")
    monkeypatch.setattr(lab2.run, "harbor_command",
                        lambda *args: ["bash", "-c", "echo progress; echo harbor-broke >&2; exit 3"])
    results = run("A", ["calc", "second"], command="python -m lab2 run --alias A --tasks calc second")
    assert [r["task"] for r in results] == ["calc", "second"]
    for result in results:
        record = json.loads((lab / "jobs/A" / result["task"] / "run.json").read_text())
        assert record == result and record["exit_status"] is None and not record["valid_submission"]
        assert record["command"] == "python -m lab2 run --alias A --tasks calc second"
        [error] = record["errors"]
        assert error.startswith("RuntimeError: Harbor produced no trial result (exit 3)") and "harbor-broke" in error
        assert record["timestamps"]["started"] and record["timestamps"]["eval_finished"] is None


NEW_TEST = "from calc import double\n\n\ndef test_double_three():\n    assert double(3) == 6\n"


def test_harbor_run(lab, endpoint, tmp_path, monkeypatch):
    url, replies, requests = endpoint
    monkeypatch.setenv("TMPDIR", str(tmp_path))  # private temp dir: other test runs cannot interfere
    monkeypatch.setattr(tempfile, "tempdir", None)
    write_skill(lab, "probe", "Use for probing.")
    config = yaml.safe_load(CONFIG.read_text())
    config["model"] |= {"api_base": url, "api_key_env": "LAB2_TEST_KEY"}
    (tmp_path / "config.yaml").write_text(yaml.safe_dump(config))
    replies.extend([command("cat .skills/probe/references/probe.txt; echo key=$LAB2_TEST_KEY"),
                    command(f"cat > /app/test_new.py <<'EOF'\n{NEW_TEST}EOF"),
                    command("echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT")])

    [result] = run("A", ["calc"], ["probe"], config=tmp_path / "config.yaml", command="python -m lab2 run ...")

    job = lab / "jobs/A/calc"
    assert sorted(p.name for p in job.iterdir()) == ["config.yaml", "eval.json", "model-requests.jsonl", "prompt.md",
                                                     "run.json", "skills", "submission", "trajectory.json"]
    assert result == json.loads((job / "run.json").read_text())
    assert json.loads((job / "trajectory.json").read_text())["info"]["lab2"] == result
    assert result["exit_status"] == "Submitted" and result["errors"] == [] and result["model_calls"] == 3
    assert result["skills"] == [{"name": "probe", "description": "Use for probing.", "path": "skills/probe"}]
    assert result["model"]["api_base"] == url and all(result["timestamps"].values())
    evaluation = json.loads((job / "eval.json").read_text())
    assert evaluation["files"] == ["test_new.py"] and result["score"] == evaluation["score"] == 50.0  # double only
    observation = next(str(m["content"]) for m in json.loads((job / "trajectory.json").read_text())["messages"]
                       if "Supplementary fixture." in str(m.get("content")))
    assert "key=\n" in observation  # the API key is not visible to commands
    assert not list(tmp_path.glob("lab2-*"))  # scratch removed
