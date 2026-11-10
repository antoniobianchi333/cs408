"""Layout of skeleton/jobs/ and alias rules.

    jobs/<alias>/<id>/                 one run of a task (written by `run`)
    jobs/vanilla/<id>/                 shipped vanilla runs (read-only for students)
    jobs/submission/<type>/<id>/       copies made by `submit`

    from lab2 import jobs
    jobs.check_alias("A", writable=True)
    jobs.job_dir("A", task)            # jobs/A/<id>, or jobs/submission/<type>/<id>
    jobs.now()                         # UTC timestamp used in every record
"""
import re
from datetime import datetime, timezone
from pathlib import Path

from lab2.tasks import SKELETON, Task

JOBS_DIR = SKELETON / "jobs"
SUBMISSION = "submission"
VANILLA = "vanilla"
ALIAS = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def check_alias(alias: str, writable: bool) -> str:
    """Validate an alias; `writable` aliases (run, submit) exclude the reserved names.

    Reserved names are compared case-insensitively, so `Vanilla` cannot reach
    jobs/vanilla on a case-insensitive file system.
    """
    if not ALIAS.match(alias):
        raise ValueError(f"invalid alias {alias!r}: use letters, digits, '.', '_', '-', starting with a letter or digit")
    if writable and alias.lower() in (SUBMISSION, VANILLA):
        raise ValueError(f"alias {alias!r} is reserved; choose another alias")
    return alias


def job_dir(alias: str, task: Task) -> Path:
    if alias == SUBMISSION:
        return JOBS_DIR / SUBMISSION / task.type / task.id
    return JOBS_DIR / alias / task.id


def now() -> str:
    """UTC timestamp, ISO-8601 to the second."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
