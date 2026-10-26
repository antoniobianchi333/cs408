"""Persistent udocker filesystem with one process group per agent action."""
import os
import platform
import re
import shutil
import signal
import subprocess
import time
import uuid
from pathlib import Path

from pydantic import BaseModel, Field
from minisweagent.exceptions import Submitted
from minisweagent.utils.serialize import recursive_merge


class UdockerConfig(BaseModel):
    image: str
    repos: Path
    layers: Path
    containers: Path
    cwd: str = "/app"
    executable: str = Field(default_factory=lambda: shutil.which("udocker") or "udocker")
    timeout: int = 180
    create_timeout: int = 600
    max_output_chars: int = 20000
    env: dict[str, str] = Field(default_factory=lambda: {"GOMAXPROCS": "4", "GOFLAGS": "-p=4 -mod=readonly", "GOPROXY": "off", "GOSUMDB": "off"})
    volumes: dict[str, str] = Field(default_factory=dict)


def normalize_tree(root: Path, *, writable_files: bool = False):
    for base, dirs, files in os.walk(root):
        for p in [Path(base)] + [Path(base, n) for n in dirs + (files if writable_files else [])]:
            if not p.is_symlink():
                mode = p.stat().st_mode | (0o700 if p.is_dir() else 0o600)
                p.chmod(mode)
                if writable_files:
                    os.chown(p, -1, os.getgid())


class UdockerEnvironment:
    def __init__(self, **kwargs):
        self.config = UdockerConfig(**kwargs)
        if any(any(s in k.upper() for s in ("TOKEN", "SECRET", "PASSWORD", "API_KEY")) for k in self.config.env):
            raise ValueError("Do not pass API credentials to the task container")
        self.container_id = None
        self.name = "cs408-lab2-" + uuid.uuid4().hex[:12]
        self.host_env = {k: os.environ[k] for k in ("PATH", "HOME", "USER", "LANG", "LC_ALL", "UDOCKER_DIR") if k in os.environ}
        self.host_env.update(UDOCKER_REPOS=str(self.config.repos), UDOCKER_LAYERS=str(self.config.layers), UDOCKER_CONTAINERS=str(self.config.containers))
        self.config.containers.mkdir(parents=True, exist_ok=True)
        try:
            self._create()
        except BaseException:
            self.cleanup()
            raise

    def _create(self):
        inspect = subprocess.run([self.config.executable, "inspect", self.config.image],
                                 env=self.host_env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if inspect.returncode:
            subprocess.run([self.config.executable, "pull", self.config.image], env=self.host_env,
                           check=True, timeout=self.config.create_timeout)
        p = subprocess.Popen([self.config.executable, "create", "--name=" + self.name, self.config.image], env=self.host_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        started = time.monotonic()
        normalized = False
        while p.poll() is None:
            if time.monotonic() - started > self.config.create_timeout:
                p.kill()
                p.communicate()
                raise TimeoutError("udocker create timed out")
            if not normalized:
                children = subprocess.run(["ps", "-o", "args=", "--ppid", str(p.pid)], capture_output=True, text=True).stdout
                match = re.search(r"find (" + re.escape(str(self.config.containers)) + r"/[a-z0-9-]+/ROOT) ", children)
                if match:
                    self.container_id = Path(match[1]).parent.name
                    normalize_tree(Path(match[1]), writable_files=True)
                    normalized = True
            time.sleep(0.2)
        output = p.communicate()[0]
        if p.returncode:
            raise RuntimeError(f"udocker create failed ({p.returncode}): {output[-2000:]}")
        self.root = (self.config.containers / self.name).resolve() / "ROOT"
        if self.root.parent.parent != self.config.containers.resolve():
            raise RuntimeError("Unexpected container root")
        self.container_id = self.root.parent.name

    def execute(self, action: dict, cwd: str = "", *, timeout: int | None = None) -> dict:
        command = action.get("command", "")
        args = [self.config.executable, "run", "--nobanner", "-w", cwd or self.config.cwd]
        for source, destination in self.config.volumes.items():
            args += ["-v", source + ":" + destination]
        for key, value in self.config.env.items():
            args += ["-e", key + "=" + value]
        args += [self.name, "bash", "-c", command]
        p = subprocess.Popen(args, env=self.host_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", start_new_session=True)
        error = ""
        try:
            output = p.communicate(timeout=timeout or self.config.timeout)[0]
            code = p.returncode
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, signal.SIGKILL)
            output = p.communicate()[0]
            code, error = 124, "Command timed out; action process group terminated"
        lines = output.lstrip().splitlines(keepends=True)
        if code == 0 and lines and lines[0].strip() == "COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT":
            raise Submitted({"role": "exit", "content": "".join(lines[1:]), "extra": {"exit_status": "Submitted", "submission": "".join(lines[1:])}})
        limit = self.config.max_output_chars
        if len(output) > limit:
            output = output[:limit // 2] + "\n[output truncated]\n" + output[-limit // 2:]
        return {"output": output, "returncode": code, "exception_info": error}

    def get_template_vars(self, **kwargs):
        return recursive_merge(self.config.model_dump(mode="json"), platform.uname()._asdict(), kwargs)

    def serialize(self):
        return {"info": {"config": {"environment": self.config.model_dump(mode="json"), "environment_type": f"{self.__class__.__module__}.{self.__class__.__name__}"}}}

    def cleanup(self):
        if self.container_id is None:
            return
        target = self.config.containers / self.container_id
        if target.exists():
            normalize_tree(target)
            shutil.rmtree(target)
        alias = self.config.containers / self.name
        alias.unlink(missing_ok=True)
        self.container_id = None
