"""Lab 2 command line (run from the repository root with scripts/activate.sh sourced).

    python -m lab2 tasks
    python -m lab2 run    --alias A --tasks ID ... [--skills NAME ...] [--redo-existing]
    python -m lab2 eval   --alias A --tasks ID ... [--checkpoints FILE ...]
    python -m lab2 submit --alias A --type TYPE [--resubmit-existing]
    python -m lab2 scoreboard

Errors in the arguments (alias, task ids, skills, existing jobs) are reported
before anything runs. Errors are printed as `error: ...` with exit status 2;
`run` exits with status 1 if a task ended with an error (see its run.json).
jobs/vanilla is read-only: `eval --alias vanilla` is refused.
"""
import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path

from lab2 import jobs, scratch
from lab2.tasks import TYPES, all_tasks, load


def cmd_tasks(args):
    for task in all_tasks():
        where = "local" if task.local else task.spec["environment"]["image"]
        print(f"{task.id:<12} {task.type:<20} {task.spec['language']:<7} {where}")


def cmd_run(args):
    from lab2.model import hide_process_environment
    from lab2.run import run

    hide_process_environment()  # this process holds the API key too; agent commands must not read it
    failed = 0
    for result in run(args.alias, args.tasks, args.skills, args.redo_existing, command=args.line):
        print(f"{result['task']}: exit={result['exit_status']} valid={result['valid_submission']} "
              f"score={result['score']} -> jobs/{args.alias}/{result['task']}/")
        for error in result["errors"]:  # first line only; run.json has the full text
            print(f"  error: {error.splitlines()[0]}")
        failed += bool(result["errors"])
    return 1 if failed else 0  # exit status 1: some task ended with an error (its run.json says why)


def cmd_eval(args):
    from lab2.environments import own_images
    from lab2.evaluate import evaluate_job

    jobs.check_alias(args.alias, writable=False)
    if args.alias.lower() == jobs.VANILLA:
        raise ValueError("jobs/vanilla is read-only; copy a job to your own alias to re-evaluate it")
    selected = [load(t) for t in args.tasks]
    missing = [t.id for t in selected if not jobs.job_dir(args.alias, t).is_dir()]
    if missing:
        raise ValueError(f"no job for {', '.join(missing)} under alias {args.alias!r}")
    scratch.clean()  # leftovers of killed runs and evaluations
    with own_images():  # images pulled here are removed at the end
        for task in selected:
            files = args.checkpoints or [task.checkpoints]
            result = evaluate_job(jobs.job_dir(args.alias, task), task.id, files, task.solution)
            print(json.dumps({k: result.get(k) for k in ("task", "valid_submission", "score")}))


def cmd_submit(args):
    from lab2.submit import submit

    record = submit(args.alias, args.type, args.resubmit_existing)
    print(f"submitted {', '.join(record['tasks'])} -> jobs/submission/{args.type}/")


def cmd_scoreboard(args):
    from lab2.scoreboard import scoreboard

    print(scoreboard())


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m lab2", description="CS408 Lab 2")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("tasks", help="list the tasks").set_defaults(func=cmd_tasks)
    r = sub.add_parser("run", help="run the agent on tasks (writes jobs/ALIAS/ID/)")
    r.add_argument("--alias", required=True)
    r.add_argument("--tasks", nargs="+", required=True, metavar="ID")
    r.add_argument("--skills", nargs="+", default=[], metavar="NAME", help="skill folders under skills/; omit for vanilla")
    r.add_argument("--redo-existing", action="store_true", help="replace existing jobs of this alias")
    r.set_defaults(func=cmd_run)
    e = sub.add_parser("eval", help="re-evaluate saved jobs (writes eval.json)")
    e.add_argument("--alias", required=True)
    e.add_argument("--tasks", nargs="+", required=True, metavar="ID")
    e.add_argument("--checkpoints", nargs="+", type=Path, metavar="FILE",
                   help="checkpoints.json files, concatenated (default: the task's public checkpoints)")
    e.set_defaults(func=cmd_eval)
    s = sub.add_parser("submit", help="copy jobs of one task type into jobs/submission/TYPE/")
    s.add_argument("--alias", required=True)
    s.add_argument("--type", required=True, choices=TYPES)
    s.add_argument("--resubmit-existing", action="store_true", help="replace an existing submission")
    s.set_defaults(func=cmd_submit)
    sub.add_parser("scoreboard", help="table of the scores of every alias on every task").set_defaults(
        func=cmd_scoreboard)
    return p


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    args = parser().parse_args(argv)
    args.line = shlex.join(["python", "-m", "lab2", *argv])  # recorded by `run`
    try:
        return args.func(args) or 0
    except (ValueError, OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
