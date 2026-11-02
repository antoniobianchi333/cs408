"""Harbor agent: the course mini-swe-agent configuration.

The agent loop runs on the host: the vendored mini-swe-agent DefaultAgent with
PurdueRCACModel and the settings in config.yaml. Only commands go through the
Harbor environment (`environment.exec`). The API key stays on the host: it is
filtered from command environments, and the agent process is made
non-dumpable before the run so commands cannot read it from /proc.

Agent kwargs (`harbor run --ak key=value`, set by lab2.run):
    config   course config YAML (default config.yaml)
    skills   JSON list of skill folders (default [] = vanilla)

Writes to the trial's agent log folder: trajectory.json, model-requests.jsonl,
prompt.md, skills/ (selected skills) and agent.json, the outcome only (exit
status, error, agent start/end, model calls, token usage; lab2.run folds it
into run.json).
"""
import asyncio
import json
import platform
from pathlib import Path

import yaml
from harbor.agents.base import BaseAgent
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext

from lab2 import skills as skill_files
from lab2.jobs import now
from lab2.model import hide_process_environment
from lab2.tasks import SKELETON

ACTION_TIMEOUT = 180  # seconds per agent command
MAX_OUTPUT_CHARS = 20000  # command output shown to the model (head and tail kept)
SUBMIT = "COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"


class HarborShim:
    """mini-swe-agent's environment protocol on top of a Harbor environment.

    mini-swe-agent is synchronous and runs in a worker thread; each command is
    scheduled on Harbor's event loop.
    """

    def __init__(self, environment: BaseEnvironment, loop: asyncio.AbstractEventLoop, cwd: str):
        self.environment, self.loop, self.cwd = environment, loop, cwd

    def execute(self, action: dict, cwd: str = "", *, timeout: int | None = None) -> dict:
        from minisweagent.exceptions import Submitted

        result = asyncio.run_coroutine_threadsafe(self.environment.exec(
            action.get("command", ""), cwd=cwd or self.cwd, timeout_sec=timeout or ACTION_TIMEOUT), self.loop).result()
        output = (result.stdout or "") + (result.stderr or "")
        lines = output.lstrip().splitlines(keepends=True)
        if result.return_code == 0 and lines and lines[0].strip() == SUBMIT:
            rest = "".join(lines[1:])
            raise Submitted({"role": "exit", "content": rest, "extra": {"exit_status": "Submitted", "submission": rest}})
        if len(output) > MAX_OUTPUT_CHARS:
            output = output[:MAX_OUTPUT_CHARS // 2] + "\n[output truncated]\n" + output[-MAX_OUTPUT_CHARS // 2:]
        error = "Command timed out; action process group terminated" if result.return_code == 124 else ""
        return {"output": output, "returncode": result.return_code, "exception_info": error}

    def get_template_vars(self, **kwargs):
        from minisweagent.utils.serialize import recursive_merge

        return recursive_merge({"cwd": self.cwd, "timeout": ACTION_TIMEOUT}, platform.uname()._asdict(), kwargs)

    def serialize(self):
        return {"info": {"config": {"environment": {"cwd": self.cwd, "backend": "harbor"},
                                    "environment_type": f"{__name__}.HarborShim"}}}


class CS408MiniSweAgent(BaseAgent):
    def __init__(self, *args, config: str | None = None, skills: list[str] | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._config = Path(config) if config else SKELETON / "config.yaml"
        self._skills = [skill_files.parse(Path(folder)) for folder in skills or []]

    @staticmethod
    def name() -> str:
        return "cs408-mini-swe-agent"

    def version(self) -> str | None:
        import minisweagent

        return minisweagent.__version__

    async def setup(self, environment: BaseEnvironment) -> None:
        return None

    async def run(self, instruction: str, environment: BaseEnvironment, context: AgentContext) -> None:
        hide_process_environment()
        out = Path(self.logs_dir)
        out.mkdir(parents=True, exist_ok=True)
        workdir = environment.task_env_config.workdir or "/app"
        if self._skills:
            skill_files.snapshot(self._skills, out / "skills")
            await environment.upload_dir(out / "skills", f"{workdir}/{skill_files.MOUNT}")
        result = await asyncio.to_thread(self._run_sync, instruction, environment, asyncio.get_running_loop(),
                                         workdir, out)
        usage = result["usage"] or {}
        context.n_input_tokens = usage.get("known_input_tokens")
        context.n_output_tokens = usage.get("known_output_tokens")

    def _run_sync(self, instruction, environment, loop, workdir, out: Path) -> dict:
        from minisweagent.agents.default import DefaultAgent
        from minisweagent.models import get_model

        config = yaml.safe_load(self._config.read_text())
        model_config = config["model"] | {"usage_log_path": str(out / "model-requests.jsonl")}
        agent_config = config["agent"] | {"output_path": str(out / "trajectory.json")}
        (out / "prompt.md").write_text(instruction)
        result = {"agent_started_at": now(), "exit_status": None, "error": None}
        model = agent = None
        try:
            model = get_model(config=model_config)
            agent = DefaultAgent(model, HarborShim(environment, loop, workdir), **agent_config)
            result["exit_status"] = agent.run(instruction, skills_catalog=skill_files.catalog(self._skills)).get("exit_status")
        except Exception as error:  # recorded, then re-raised so Harbor records the trial exception too
            result["error"] = f"{type(error).__name__}: {error}"
            raise
        finally:
            result["agent_finished_at"] = now()
            result["model_calls"] = getattr(agent, "n_calls", 0)
            result["usage"] = model.usage_summary() if hasattr(model, "usage_summary") else None
            (out / "agent.json").write_text(json.dumps(result, indent=2) + "\n")
        return result
