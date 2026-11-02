"""Evaluation of saved jobs: re-runs verify.py on a job's submission.

    python -m lab2 eval --alias A --tasks paperless [--checkpoints FILE ...]

    from lab2.evaluate import evaluate_job, stage_verifier
    evaluate_job(job_dir, "paperless", [task.checkpoints])   # writes job_dir/eval.json

The submission (job_dir/submission/) is copied into a fresh environment (a new
udocker container of the task image, or a new workspace for the warmup), the
verifier payload is staged next to it, and verify.py writes the evaluation,
stamped with "evaluated_at". stage_verifier also builds the collect-only
payload that Harbor runs after the agent (lab2.run).
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

from lab2 import scratch
from lab2.jobs import now
from lab2.tasks import Task, load

VERIFY = Path(__file__).with_name("verify.py")
TEST_SH = '#!/bin/bash\nexec python3 "${CS408_TESTS:-/tests}/verify.py"\n'


def merge_checkpoints(task: Task, files: list[Path]) -> dict:
    """Concatenate checkpoints.json files of one task; checkpoint ids must be unique."""
    checkpoints = []
    for path in files:
        if not Path(path).is_file():
            raise ValueError(f"checkpoints file {path} does not exist")
        data = json.loads(Path(path).read_text())
        if data.get("task") != task.id:
            raise ValueError(f"{path} is for task {data.get('task')!r}, not {task.id!r}")
        if not isinstance(data.get("checkpoints"), list):
            raise ValueError(f"{path}: 'checkpoints' must be a list")
        for checkpoint in data["checkpoints"]:
            versions = checkpoint.get("faulty_versions") if isinstance(checkpoint, dict) else None
            if not isinstance(versions, list) or "id" not in checkpoint or \
                    any(not isinstance(v, dict) or "id" not in v or "patch" not in v for v in versions):
                raise ValueError(f"{path}: each checkpoint needs 'id' and 'faulty_versions', "
                                 "a list of objects with 'id' and 'patch'")
        checkpoints += data["checkpoints"]
    ids = [c["id"] for c in checkpoints]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        raise ValueError(f"duplicate checkpoint ids: {', '.join(duplicates)}")
    return {"task": task.id, "checkpoints": checkpoints}


def stage_verifier(task: Task, dest: Path, checkpoint_files: list[Path], solution: Path | None = None,
                   extra_editable: list[str] = (), collect_only: bool = False) -> Path:
    """Write the verifier payload: verify.py, test.sh, task.json, checkpoints.json [, solution.patch].

    collect_only: verify.py only collects the submission (no test runs).
    """
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(VERIFY, dest / "verify.py")
    (dest / "test.sh").write_text(TEST_SH)
    (dest / "test.sh").chmod(0o755)
    spec = task.spec
    info = {"id": task.id, "type": task.type, "language": spec["language"], "workdir": task.workdir,
            "test_paths": spec["test_paths"], "editable": list(spec.get("editable") or []) + list(extra_editable),
            "head": spec["environment"]["head"], "check": spec.get("check") or {}, "collect_only": collect_only}
    (dest / "task.json").write_text(json.dumps(info, indent=2) + "\n")
    (dest / "checkpoints.json").write_text(json.dumps(merge_checkpoints(task, checkpoint_files), indent=1) + "\n")
    if solution:
        shutil.copyfile(solution, dest / "solution.patch")
    return dest


def _copy_submission(job_dir: Path, app: Path) -> None:
    source = job_dir / "submission"
    if source.is_dir():
        shutil.copytree(source, app, dirs_exist_ok=True)


def _verify_local(task: Task, job_dir: Path, tests: Path, out: Path, tmp: Path) -> None:
    from lab2.environments import create_workspace, local_env

    root = create_workspace(task.dir / task.spec["environment"]["project"], tmp / "workspace")
    _copy_submission(job_dir, root / "app")
    env = local_env(root / "app", tests, out)
    subprocess.run([sys.executable, str(tests / "verify.py")], env=env, check=True, stdout=subprocess.DEVNULL)


def _verify_image(task: Task, job_dir: Path, tests: Path, out: Path) -> None:
    from lab2.environments import Udocker

    udocker = Udocker()
    env = task.spec["environment"]
    udocker.ensure_image(env["image"], env.get("archive"))
    name = scratch.name("eval")
    try:
        root = udocker.create(name, env["image"])
        _copy_submission(job_dir, root / task.workdir.lstrip("/"))
        args = udocker.run_args(name, task.workdir, task.env, {str(tests): "/tests", str(out): "/logs/verifier"})
        subprocess.run(args + ["python3", "/tests/verify.py"], env=udocker.env, check=True, stdout=subprocess.DEVNULL)
    finally:
        udocker.remove(name)


def evaluate_job(job_dir: Path, task_id: str, checkpoint_files: list[Path], solution: Path | None = None,
                 out_name: str = "eval.json", extra_editable: list[str] = ()) -> dict:
    """Re-run verify.py for a saved job and write job_dir/out_name.

    extra_editable: diagnostic only, accepts edits to these existing test files
    (used to replay reference tests that extend starter tests).
    """
    task, job_dir = load(task_id), Path(job_dir).resolve()
    if not job_dir.is_dir():
        raise ValueError(f"no job at {job_dir}")
    with scratch.temporary_directory("eval") as name:
        tmp = Path(name)
        tests, out = stage_verifier(task, tmp / "tests", checkpoint_files, solution, extra_editable), tmp / "out"
        out.mkdir()
        if task.local:
            _verify_local(task, job_dir, tests, out, tmp)
        else:
            _verify_image(task, job_dir, tests, out)
        result = json.loads((out / "eval.json").read_text())
    result["evaluated_at"] = now()
    run = job_dir / "run.json"
    if run.exists():  # how the job itself ended, for context next to the evaluation
        result["job"] = {k: json.loads(run.read_text()).get(k) for k in ("alias", "skills", "exit_status", "errors")}
    (job_dir / out_name).write_text(json.dumps(result, indent=2) + "\n")
    return result
