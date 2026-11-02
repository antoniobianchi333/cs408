"""`submit`: copy an alias's jobs of one task type into jobs/submission/<type>/.

    python -m lab2 submit --alias A --type test-writing [--resubmit-existing]

Every task of the type must have a job jobs/A/<id>/, and all of them must have
used the same skills (identical skills/ snapshots; vanilla = none). The copies
go to jobs/submission/<type>/<id>/ together with submission.json (alias, tasks,
skills, time).
"""
import json
import shutil

from pathlib import Path

from lab2 import jobs
from lab2.tasks import TYPES, all_tasks


def skills_snapshot(job: Path) -> dict[str, bytes]:
    """The job's skills/ snapshot as {relative path: content}; empty for vanilla."""
    folder = job / "skills"
    return {str(p.relative_to(folder)): p.read_bytes() for p in sorted(folder.rglob("*")) if p.is_file()}


def submit(alias: str, kind: str, resubmit_existing: bool = False) -> dict:
    jobs.check_alias(alias, writable=True)
    if kind not in TYPES:
        raise ValueError(f"unknown type {kind!r}; choose one of {', '.join(TYPES)}")
    selected = [t for t in all_tasks() if t.type == kind]
    missing = [t.id for t in selected if not jobs.job_dir(alias, t).is_dir()]
    if missing:
        raise ValueError(f"jobs/{alias}/ has no job for {', '.join(missing)}; run them first")
    snapshots = {t.id: skills_snapshot(jobs.job_dir(alias, t)) for t in selected}
    if len({tuple(sorted(s.items())) for s in snapshots.values()}) > 1:
        used = "; ".join(f"{t}: {' '.join(sorted({path.split('/')[0] for path in s})) or 'no skills'}"
                         for t, s in snapshots.items())
        raise ValueError(f"the {kind} jobs of {alias!r} must use the same skills ({used})")
    dest = jobs.JOBS_DIR / jobs.SUBMISSION / kind
    if dest.exists():
        if not resubmit_existing:
            raise ValueError(f"{dest.relative_to(jobs.JOBS_DIR.parent)} exists; pass --resubmit-existing to replace it")
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    for task in selected:
        shutil.copytree(jobs.job_dir(alias, task), dest / task.id)
    run = jobs.job_dir(alias, selected[0]) / "run.json"
    skills = json.loads(run.read_text()).get("skills", []) if run.exists() else []
    record = {"alias": alias, "type": kind, "tasks": [t.id for t in selected], "skills": skills,
              "submitted_at": jobs.now()}
    (dest / "submission.json").write_text(json.dumps(record, indent=2) + "\n")
    return record
