"""The scoreboard over a synthetic jobs tree of made-up tasks."""
import json

from conftest import write_task
from test_cli import cli


def job(lab, path, score=0.0, evaluated=True):
    folder = lab / "jobs" / path
    folder.mkdir(parents=True)
    if evaluated:
        (folder / "eval.json").write_text(json.dumps({"score": score}))


def test_scoreboard(lab, capsys):
    write_task(lab, "tw", "test-writing")
    write_task(lab, "ir", "issue-reproduction")
    job(lab, "vanilla/calc", 50)
    code, out, _ = cli(capsys, "scoreboard")
    assert code == 0 and out.splitlines()[0].split() == ["alias", "calc", "tw", "ir", "TW", "mean", "IR", "mean"]
    assert out.splitlines()[1].split() == ["vanilla", "50.00", "–", "–", "–", "–"]

    job(lab, "B/tw", 10)
    job(lab, "B/ir", 30)
    job(lab, "A/ir", None)
    job(lab, "A/tw", evaluated=False)
    job(lab, "submission/warmup/calc", 100)
    code, out, _ = cli(capsys, "scoreboard")
    rows = [line.split() for line in out.splitlines()[1:]]
    assert [row[0] for row in rows] == ["vanilla", "A", "B"]  # vanilla first, submission skipped
    assert rows[1] == ["A", "–", "no", "eval", "checks", "–", "–"]
    assert rows[2] == ["B", "–", "10.00", "30.00", "10.00", "30.00"]


def test_scoreboard_without_jobs(lab, capsys):
    assert "no jobs under" in cli(capsys, "scoreboard")[1]
