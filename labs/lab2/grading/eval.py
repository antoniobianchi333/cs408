"""TA evaluation with all checkpoints (public and hidden).

    source skeleton/scripts/activate.sh
    python grading/eval.py --alias A --tasks paperless dateutil ...

For each task, re-evaluates the job skeleton/jobs/<alias>/<id>/ (alias
`submission`: jobs/submission/<type>/<id>/; `vanilla` is read, never changed
except for the added eval-full.json) with grading/tasks/<type>/<id>/checkpoints.json
and, for issue reproduction, the task's reference repair (skeleton solution.patch). Writes
eval-full.json next to the job's eval.json, which stays untouched. Errors are
printed as `error: ...` with exit status 2.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

GRADING = Path(__file__).resolve().parent
sys.path.insert(0, str(GRADING.parent / "skeleton"))

from lab2 import jobs, scratch  # noqa: E402
from lab2.environments import own_images  # noqa: E402
from lab2.evaluate import evaluate_job  # noqa: E402
from lab2.tasks import load  # noqa: E402


def evaluate(alias: str, task_ids: list[str]) -> None:
    jobs.check_alias(alias, writable=False)
    selected = [load(t) for t in task_ids]
    scratch.clean()  # leftovers of killed runs and evaluations
    with own_images():  # images pulled here are removed at the end
        for task in selected:
            checkpoints = GRADING / "tasks" / task.type / task.id / "checkpoints.json"  # public + hidden
            result = evaluate_job(jobs.job_dir(alias, task), task.id, [checkpoints], task.solution,
                                  out_name="eval-full.json")
            print(json.dumps({k: result.get(k) for k in ("task", "valid_submission", "score", "public_score", "hidden_score")}))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--alias", required=True)
    parser.add_argument("--tasks", nargs="+", required=True, metavar="ID")
    args = parser.parse_args(argv)
    try:
        evaluate(args.alias, args.tasks)
    except (ValueError, OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
