"""`scoreboard`: the score of every alias on every task, from the jobs under jobs/.

    python -m lab2 scoreboard

    from lab2.scoreboard import scoreboard
    print(scoreboard())

One row per alias (vanilla first, then by name; jobs/submission is skipped),
one column per task in registry order. A cell is the score in the job's
eval.json, or:

    –         no job for the task
    no eval   a job without eval.json
    checks    an eval.json without a score

"TW mean" and "IR mean" average the test-writing and the issue-reproduction
tasks, each only when all tasks of that part have a score.
"""
import json
import statistics

from lab2 import jobs
from lab2.tasks import Task, all_tasks

NO_JOB, NO_EVAL, CHECKS = "–", "no eval", "checks"
MEANS = (("TW mean", "test-writing"), ("IR mean", "issue-reproduction"))  # (column, task type)


def score(alias: str, task: Task) -> float | str:
    """The score of jobs/<alias>/<id>/, or the text shown in its place."""
    job = jobs.job_dir(alias, task)
    if not job.is_dir():
        return NO_JOB
    if not (job / "eval.json").exists():
        return NO_EVAL
    value = json.loads((job / "eval.json").read_text()).get("score")
    return CHECKS if value is None else value


def aliases() -> list[str]:
    """Alias folders under jobs/, vanilla first."""
    if not jobs.JOBS_DIR.is_dir():
        return []
    names = [p.name for p in jobs.JOBS_DIR.iterdir() if p.is_dir() and p.name.lower() != jobs.SUBMISSION]
    return sorted(names, key=lambda name: (name != jobs.VANILLA, name))


def scoreboard() -> str:
    """The table as text: a header, then one aligned row per alias."""
    tasks = all_tasks()
    header = ["alias", *(t.id for t in tasks), *(name for name, _ in MEANS)]
    rows = []
    for alias in aliases():
        scores = [score(alias, t) for t in tasks]
        means = []
        for _, kind in MEANS:
            part = [s for s, t in zip(scores, tasks) if t.type == kind]
            means.append(statistics.mean(part) if part and all(isinstance(s, (int, float)) for s in part) else NO_JOB)
        rows.append([alias, *(s if isinstance(s, str) else f"{s:.2f}" for s in [*scores, *means])])
    if not rows:
        return f"no jobs under {jobs.JOBS_DIR}"
    widths = [max(len(row[i]) for row in [header, *rows]) for i in range(len(header))]
    return "\n".join("  ".join([row[0].ljust(widths[0]), *(c.rjust(w) for c, w in zip(row[1:], widths[1:]))])
                     for row in [header, *rows])
