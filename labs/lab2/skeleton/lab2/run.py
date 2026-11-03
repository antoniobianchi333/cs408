"""`run`: one agent run per task through Harbor, collected into jobs/<alias>/<id>/.

    python -m lab2 run --alias A --tasks paperless k6 [--skills NAME ...] [--redo-existing]

Before any run, every needed task image is found in the shared store or
pulled into the user's store, one at a time (removed when the command ends).
For each task: export a Harbor task folder (instruction, task.toml and a
collect-only verifier payload) into a scratch folder under the system temp
directory, run `harbor run` with lab2.agent and lab2.environments (its console
output is captured; the tail is kept for error messages), copy the results into
jobs/<alias>/<id>/ and delete the scratch folder. The Harbor verifier only
collects the accepted test files; the submission is then evaluated with the
task's public checkpoints in a fresh environment (lab2.evaluate.evaluate_job),
so eval.json never depends on what the agent left in its environment:

    run.json  trajectory.json  model-requests.jsonl  prompt.md  config.yaml  [skills/]  submission/  eval.json

run.json records every parameter of the run (command line, alias, skills with
their descriptions and snapshot paths, timestamps, effective model/agent
settings, image, software versions, repository commit, host) and its outcome;
the same record is stored in trajectory.json under info.lab2, so a trajectory
alone shows how it was made. A task whose Harbor run or evaluation fails still
gets run.json (exit_status null, the error in "errors"); the other tasks go on.
"""
import json
import os
import platform
import shutil
import subprocess
from pathlib import Path

import yaml

from lab2 import jobs, scratch, skills
from lab2.evaluate import evaluate_job, stage_verifier
from lab2.tasks import SKELETON, Task, load

AGENT = "lab2.agent:CS408MiniSweAgent"
CONFIG = SKELETON / "config.yaml"
OUTPUT_TAIL = 3000  # characters of Harbor's console output kept in an error message


def toml(value) -> str:
    return json.dumps(value)  # JSON strings, numbers and booleans are valid TOML values


def export(task: Task, dest: Path, config: dict) -> Path:
    """Write the Harbor task folder for `task` into dest."""
    (dest / "environment").mkdir(parents=True)
    (dest / "instruction.md").write_text(task.prompt())
    # The agent's own wall-time limit ends the run first; Harbor's timeout is a backstop.
    agent_timeout = float(config["agent"].get("wall_time_limit_seconds") or 7200) + 1800
    lines = ['schema_version = "1.1"', "", "[task]", f"name = {toml('cs408-lab2/' + task.id)}", "",
             "[agent]", f"timeout_sec = {agent_timeout}", "", "[verifier]", "timeout_sec = 600.0", "",
             "[environment]", f"workdir = {toml(task.workdir)}", "build_timeout_sec = 3600.0"]
    if not task.local:
        image = task.spec["environment"]["image"]
        lines.append(f"docker_image = {toml(image)}")
        (dest / "environment" / "Dockerfile").write_text(f"FROM {image}\n")
    if task.env:
        lines += ["", "[environment.env]"] + [f"{toml(k)} = {toml(v)}" for k, v in task.env.items()]
    if task.spec.get("prepare"):
        lines += ["", "[environment.healthcheck]", f"command = {toml(f'cd {task.workdir} && ' + task.spec['prepare'])}",
                  "timeout_sec = 600.0", "retries = 0"]
    (dest / "task.toml").write_text("\n".join(lines) + "\n")
    stage_verifier(task, dest / "tests", [], collect_only=True)  # scored afterwards by evaluate_job
    return dest


def harbor_command(task: Task, task_dir: Path, jobs_dir: Path, selected: list[skills.Skill], config: Path) -> list[str]:
    if task.local:
        environment = ["-e", "lab2.environments:LocalEnvironment",
                       "--ek", f"project={task.dir / task.spec['environment']['project']}"]
    else:
        environment = ["-e", "lab2.environments:UdockerEnvironment"]
    return ["harbor", "run", "-p", str(task_dir), "-a", AGENT, *environment,
            "--ak", f"config={config}", "--ak", f"skills={json.dumps([str(s.dir) for s in selected])}",
            "-o", str(jobs_dir), "--job-name", task.id, "-n", "1", "-k", "1"]


def git_commit() -> dict:
    """The repository's git commit and whether its working tree has changes."""
    def git(*args):
        out = subprocess.run(["git", "-C", str(SKELETON), *args], capture_output=True, text=True)
        return out.stdout.strip() if out.returncode == 0 else None
    status = git("status", "--porcelain", "--", ".")
    return {"commit": git("rev-parse", "HEAD"), "dirty": bool(status) if status is not None else None}


def versions() -> dict:
    import harbor
    import minisweagent

    return {"python": platform.python_version(), "mini-swe-agent": minisweagent.__version__,
            "harbor": getattr(harbor, "__version__", None)}


def model_settings(config: dict) -> dict:
    """Effective model settings: PurdueRCACConfig defaults overridden by config.yaml.

    Templates and the per-run log path are left out. Credentials are never in
    the settings: api_key_env only names the variable holding the key.
    """
    from lab2.model import PurdueRCACConfig

    merged = PurdueRCACConfig().model_dump(mode="json") | config["model"]
    return {k: v for k, v in merged.items() if not k.endswith("_template") and k != "usage_log_path"}


def parameters(alias: str, task: Task, selected: list[skills.Skill], redo_existing: bool, config: dict,
               command: str | None) -> dict:
    """Everything that determines the run, recorded before it starts."""
    env = task.spec["environment"]
    return {"command": command, "alias": alias, "task": task.id, "type": task.type, "redo_existing": redo_existing,
            "skills": [{"name": s.name, "description": s.description, "path": f"skills/{s.name}"} for s in selected],
            "model": model_settings(config),
            "agent": {k: v for k, v in config["agent"].items() if not k.endswith("_template")},
            "environment": ({"local": True, "head": env["head"]} if task.local else
                            {"image": env["image"], "head": env["head"]}),
            "versions": versions(), "repository": git_commit(),
            "host": {"name": platform.node(), "platform": platform.platform()}}


def collect(trial: Path, dest: Path) -> tuple[dict, list[str]]:
    """Copy one Harbor trial's agent files and collected submission into dest.

    Returns the agent outcome (agent.json) and the errors of the trial.
    """
    for source in ("agent/trajectory.json", "agent/model-requests.jsonl", "agent/prompt.md", "agent/skills",
                   "verifier/submission"):
        path, target = trial / source, dest / Path(source).name
        if path.is_dir():
            shutil.copytree(path, target)
        elif path.is_file():
            shutil.copyfile(path, target)
    trial_result = json.loads((trial / "result.json").read_text())
    agent = json.loads((trial / "agent/agent.json").read_text()) if (trial / "agent/agent.json").exists() else {}
    exception = trial_result.get("exception_info")
    errors = [agent.get("error")] + ([f"{exception['exception_type']}: {exception['exception_message']}"]
                                     if exception else [])
    return agent, [e for e in errors if e]


def run_task(alias: str, task: Task, selected: list[skills.Skill], config: Path = CONFIG,
             redo_existing: bool = False, command: str | None = None) -> dict:
    """Run, collect and evaluate one task; jobs/<alias>/<id>/run.json is written even if a step fails."""
    dest = jobs.job_dir(alias, task)
    started = jobs.now()
    settings = yaml.safe_load(config.read_text())
    record = {**parameters(alias, task, selected, redo_existing, settings, command),
              "timestamps": {"started": started, "agent_started": None, "agent_finished": None,
                             "eval_finished": None, "finished": None},
              "exit_status": None, "model_calls": None, "usage": None, "valid_submission": False, "score": None,
              "errors": []}
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    shutil.copyfile(config, dest / "config.yaml")
    try:
        with scratch.temporary_directory("run") as name:
            work = Path(name)
            task_dir = export(task, work / "task" / task.id, settings)
            env = dict(os.environ, PYTHONPATH=str(SKELETON), PYTHONDONTWRITEBYTECODE="1")
            harbor = subprocess.run(harbor_command(task, task_dir, work / "jobs", selected, config), env=env,
                                    capture_output=True, text=True)
            trials = [p for p in (work / "jobs" / task.id).glob("*/") if (p / "result.json").exists()]
            if not trials:
                raise RuntimeError(f"Harbor produced no trial result (exit {harbor.returncode}):\n"
                                   + (harbor.stdout + harbor.stderr)[-OUTPUT_TAIL:])
            agent, record["errors"] = collect(trials[0], dest)
        record["timestamps"].update(agent_started=agent.get("agent_started_at"),
                                    agent_finished=agent.get("agent_finished_at"))
        record.update(exit_status=agent.get("exit_status"), model_calls=agent.get("model_calls"),
                      usage=agent.get("usage"))
        evaluation = evaluate_job(dest, task.id, [task.checkpoints], task.solution)
        record["timestamps"]["eval_finished"] = evaluation["evaluated_at"]
        record.update(valid_submission=bool(evaluation["valid_submission"]), score=evaluation["score"])
    except Exception as error:  # recorded in run.json; the other tasks continue
        record["errors"].append(f"{type(error).__name__}: {error}")
    record["timestamps"]["finished"] = jobs.now()
    record["errors"] = list(dict.fromkeys(record["errors"]))
    (dest / "run.json").write_text(json.dumps(record, indent=2) + "\n")
    trajectory = dest / "trajectory.json"
    if trajectory.exists():
        data = json.loads(trajectory.read_text())
        data.setdefault("info", {})["lab2"] = record
        trajectory.write_text(json.dumps(data, indent=2) + "\n")
    return record


def run(alias: str, task_ids: list[str], skill_names: list[str] = (), redo_existing: bool = False,
        config: Path = CONFIG, command: str | None = None) -> list[dict]:
    """Validate everything first, load the images, then run the tasks one after another.

    Tasks never run at once: every run holds a full container copy (~100k inodes),
    and the shared /tmp of a school machine serves many students at the same time.

    command: the command line to record (lab2.__main__ passes the CLI's).
    """
    from lab2.environments import Udocker, own_images

    jobs.check_alias(alias, writable=True)
    selected = [load(t) for t in dict.fromkeys(task_ids)]
    selected_skills = skills.resolve(list(skill_names))
    settings = yaml.safe_load(Path(config).read_text())
    if not isinstance(settings, dict) or not {"model", "agent"} <= set(settings):
        raise ValueError(f"{config} needs 'model' and 'agent' sections")
    existing = [t.id for t in selected if jobs.job_dir(alias, t).exists()]
    if existing and not redo_existing:
        raise ValueError(f"jobs/{alias}/ already has {', '.join(existing)}; pass --redo-existing to replace")
    images = list(dict.fromkeys(t.spec["environment"]["image"] for t in selected if not t.local))
    scratch.clean()  # leftovers of killed runs and evaluations
    with own_images():  # images pulled here are removed at the end
        for image in images:  # shared copy, or pulled once for this command
            Udocker().ensure_image(image)
        return [run_task(alias, t, selected_skills, config, redo_existing, command) for t in selected]
