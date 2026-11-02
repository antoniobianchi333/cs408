"""Task environments for Harbor and for re-evaluation.

UdockerEnvironment   image tasks: one rootless udocker container per trial.
LocalEnvironment     the warmup (garage): a git workspace on the host.

Harbor loads them by import path (`harbor run -e lab2.environments:...`, see
lab2.run). The udocker helpers below are also used by lab2.evaluate.

Image store: $LAB2_IMAGE_STORE, default .cache/udocker (repos/,
layers/, containers/). A task image missing from the store is loaded from its
archive, images/<environment.archive>.
"""
import asyncio
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath

from harbor.environments.base import BaseEnvironment, ExecResult
from harbor.environments.capabilities import EnvironmentCapabilities, EnvironmentResourceCapabilities
from harbor.models.environment_type import EnvironmentType

from lab2 import scratch
from lab2.skills import MOUNT
from lab2.tasks import SKELETON

IMAGES_DIR = SKELETON / "images"
OUTPUT_LIMIT = 4_000_000  # characters of stdout/stderr kept per command
SECRET = re.compile(r"KEY|TOKEN|SECRET|PASSWORD", re.I)
# Fixed identity, dates and no user/system git config: the workspace commit of
# a local task has the same hash everywhere (task.yaml environment.head).
WORKSPACE_GIT = {"GIT_AUTHOR_NAME": "CS408", "GIT_AUTHOR_EMAIL": "cs408@localhost",
                 "GIT_AUTHOR_DATE": "2026-01-01T00:00:00+00:00", "GIT_COMMITTER_NAME": "CS408",
                 "GIT_COMMITTER_EMAIL": "cs408@localhost", "GIT_COMMITTER_DATE": "2026-01-01T00:00:00+00:00",
                 "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}


def image_store() -> Path:
    return Path(os.environ.get("LAB2_IMAGE_STORE") or SKELETON / ".cache" / "udocker").resolve()


def normalize_tree(root: Path, writable_files: bool = False) -> None:
    """Make an extracted container tree owner-accessible (and removable).

    Image layers may contain read-only directories; udocker extracts them
    as-is, which blocks writes inside the container and `rm -rf` afterwards.
    """
    for base, dirs, files in os.walk(root):
        for p in [Path(base)] + [Path(base, n) for n in dirs + (files if writable_files else [])]:
            if not p.is_symlink():
                p.chmod(p.stat().st_mode | (0o700 if p.is_dir() else 0o600))
                if writable_files:
                    os.chown(p, -1, os.getgid())


class Udocker:
    """Synchronous udocker commands against one image store."""

    def __init__(self, store: Path | None = None):
        self.store = Path(store or image_store()).resolve()
        self.executable = shutil.which("udocker") or "udocker"
        self.env = {k: os.environ[k] for k in ("PATH", "HOME", "USER", "LANG", "LC_ALL", "UDOCKER_DIR") if k in os.environ}
        self.env.update({"UDOCKER_" + d.upper(): str(self.store / d) for d in ("repos", "layers", "containers")})

    def command(self, *args: str) -> list[str]:
        return [self.executable, "--quiet", *args]

    def call(self, *args: str, timeout: float = 3600) -> str:
        p = subprocess.run(self.command(*args), env=self.env, capture_output=True, text=True, timeout=timeout)
        if p.returncode:
            raise RuntimeError(f"udocker {' '.join(args[:2])} failed ({p.returncode}): {(p.stdout + p.stderr)[-2000:]}")
        return p.stdout

    def has_image(self, image: str) -> bool:
        return subprocess.run(self.command("inspect", image), env=self.env, capture_output=True).returncode == 0

    def ensure_image(self, image: str, archive: str | None) -> None:
        for d in ("repos", "layers", "containers"):
            (self.store / d).mkdir(parents=True, exist_ok=True)
        if self.has_image(image):
            return
        path = IMAGES_DIR / archive if archive else None
        if path is None or not path.is_file():
            raise RuntimeError(f"image {image} is not in {self.store}; put {archive or 'its archive'} into {IMAGES_DIR}")
        self.call("load", "-i", str(path))

    def create(self, name: str, image: str) -> Path:
        """Create container `name`; returns its root directory on the host."""
        self.call("create", f"--name={name}", image)
        root = (self.store / "containers" / name).resolve() / "ROOT"
        normalize_tree(root, writable_files=True)
        return root

    def remove(self, name: str) -> None:
        alias = self.store / "containers" / name
        if alias.exists():
            target = alias.resolve()
            normalize_tree(target)
            shutil.rmtree(target, ignore_errors=True)
        alias.unlink(missing_ok=True)

    def run_args(self, name: str, workdir: str, env: dict[str, str], volumes: dict[str, str] | None = None) -> list[str]:
        args = self.command("run", "--nobanner", "-w", workdir)
        for source, target in (volumes or {}).items():
            args += ["-v", f"{source}:{target}"]
        for key, value in env.items():
            args += ["-e", f"{key}={value}"]
        return args + [name]


def create_workspace(project: Path, root: Path) -> Path:
    """Local task workspace: root/app (project copy, one deterministic git commit), root/tests, root/logs/*."""
    app = root / "app"
    shutil.copytree(project, app)
    for d in ("tests", "logs/agent", "logs/verifier", "logs/artifacts"):
        (root / d).mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, **WORKSPACE_GIT)

    def git(*args):
        subprocess.run(["git", "-C", str(app), *args], env=env, check=True, capture_output=True)

    git("init", "-q")
    (app / ".git" / "info" / "exclude").write_text(f"{MOUNT}/\n__pycache__/\n.pytest_cache/\n")
    git("add", ".")
    git("commit", "-qm", "Task baseline")
    return root


def local_env(app: Path, tests: Path, out: Path, extra: dict[str, str] | None = None) -> dict[str, str]:
    """Environment of commands in a local workspace (agent commands and verify.py).

    The host environment without credential variables, plus `extra`; then the
    repository venv first on PATH (python3 is the venv Python, which has pytest),
    PYTHONDONTWRITEBYTECODE=1 and CS408_APP/TESTS/OUT for verify.py.
    """
    env = {k: v for k, v in os.environ.items() if not SECRET.search(k)}
    env.update(extra or {})
    env.update(PATH=str(Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", ""),
               PYTHONDONTWRITEBYTECODE="1", CS408_APP=str(app), CS408_TESTS=str(tests), CS408_OUT=str(out))
    return env


async def _run(args: list[str], env: dict, timeout: float | None, cwd: str | None = None) -> ExecResult:
    """Run a process in its own session; on timeout kill the whole group (exit code 124)."""
    p = await asyncio.create_subprocess_exec(*args, env=env, cwd=cwd, stdout=asyncio.subprocess.PIPE,
                                             stderr=asyncio.subprocess.PIPE, start_new_session=True)
    try:
        out, err = await asyncio.wait_for(p.communicate(), timeout)
        code = p.returncode
    except (asyncio.TimeoutError, TimeoutError):
        os.killpg(p.pid, signal.SIGKILL)
        out, err = await p.communicate()
        code, err = 124, (err or b"") + f"\n[command timed out after {timeout}s]".encode()
    return ExecResult(stdout=out.decode(errors="replace")[-OUTPUT_LIMIT:],
                      stderr=err.decode(errors="replace")[-OUTPUT_LIMIT:], return_code=code)


class _HostFiles:
    """Harbor file transfer by plain copies; subclasses define `_host(path)`."""

    def _host(self, path: str) -> Path:
        raise NotImplementedError

    async def upload_file(self, source_path, target_path: str):
        dest = self._host(target_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(shutil.copyfile, source_path, dest)

    async def upload_dir(self, source_dir, target_dir: str):
        await asyncio.to_thread(shutil.copytree, source_dir, self._host(target_dir), symlinks=True, dirs_exist_ok=True)

    async def download_file(self, source_path: str, target_path):
        Path(target_path).parent.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(shutil.copyfile, self._host(source_path), target_path)

    async def download_dir(self, source_dir: str, target_dir):
        src = self._host(source_dir)
        if src.exists():
            await asyncio.to_thread(shutil.copytree, src, target_dir, symlinks=True, dirs_exist_ok=True)

    @classmethod
    def resource_capabilities(cls) -> EnvironmentResourceCapabilities:
        return EnvironmentResourceCapabilities()

    @property
    def capabilities(self) -> EnvironmentCapabilities:
        return EnvironmentCapabilities()

    @staticmethod
    def type() -> EnvironmentType:
        # Harbor has no value for these providers; selection is by import path.
        return EnvironmentType.DOCKER


class UdockerEnvironment(_HostFiles, BaseEnvironment):
    """The task image ([environment] docker_image) in a udocker container.

    Commands run with `udocker run`, so files persist between them; files are
    transferred by copying into the container root, a plain host directory.
    Environment kwargs (`--ek`): archive (file name under images/),
    store (default: image_store()).
    """

    def __init__(self, *args, archive: str | None = None, store: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._udocker = Udocker(Path(store) if store else None)
        self._archive = archive
        self._name = scratch.name("agent")
        self._root: Path | None = None

    @classmethod
    def preflight(cls) -> None:
        if shutil.which("udocker") is None:
            raise SystemExit("udocker is not on PATH; source scripts/activate.sh")

    def _validate_definition(self):
        if not self.task_env_config.docker_image:
            raise ValueError("UdockerEnvironment needs [environment] docker_image")

    def _host(self, path: str) -> Path:
        rel = PurePosixPath(path)
        if not rel.is_absolute() or ".." in rel.parts:
            raise ValueError(f"container path must be absolute without '..': {path}")
        return self._root.joinpath(*rel.parts[1:])

    async def start(self, force_build: bool) -> None:
        image = self.task_env_config.docker_image
        await asyncio.to_thread(self._udocker.ensure_image, image, self._archive)
        self._root = await asyncio.to_thread(self._udocker.create, self._name, image)
        await self.exec("mkdir -p /logs/agent /logs/verifier /logs/artifacts /tests")

    async def stop(self, delete: bool):
        if self._root is not None:
            await asyncio.to_thread(self._udocker.remove, self._name)
            self._root = None

    async def exec(self, command: str, cwd: str | None = None, env: dict[str, str] | None = None,
                   timeout_sec: int | None = None, user: str | int | None = None) -> ExecResult:
        args = self._udocker.run_args(self._name, cwd or self.task_env_config.workdir or "/", self._merge_env(env) or {})
        return await _run(args + ["bash", "-c", command], self._udocker.env, timeout_sec)


class LocalEnvironment(_HostFiles, BaseEnvironment):
    """The warmup on the host, in a fresh workspace under the system temp folder.

    Harbor and the verifier address the absolute paths used in containers; they
    map onto the workspace (in commands, working directories and transfers):

        /app    -> <workspace>/app     copy of tasks/warmup/<id>/project, git initialised
        /tests  -> <workspace>/tests   verifier payload
        /logs   -> <workspace>/logs    agent/, verifier/, artifacts/

    Commands run with local_env() (no credential variables, the repository venv
    first on PATH, CS408_APP/TESTS/OUT for verify.py). The commands are not
    sandboxed: they run as the user on the host. Environment kwarg (`--ek`):
    project (absolute path of the project folder).
    """

    ROOTS = ("app", "tests", "logs")
    PATTERN = re.compile(r"(?<![\w.~/-])/(app|tests|logs)(?=/|\b|$)")

    def __init__(self, *args, project: str, **kwargs):
        super().__init__(*args, **kwargs)
        self._project = Path(project)
        self._root: Path | None = None

    def _validate_definition(self):
        pass

    def _host(self, path: str) -> Path:
        rel = PurePosixPath(path)
        if not rel.is_absolute() or ".." in rel.parts or len(rel.parts) < 2 or rel.parts[1] not in self.ROOTS:
            raise ValueError(f"LocalEnvironment maps only /app, /tests and /logs: {path}")
        return self._root.joinpath(*rel.parts[1:])

    async def start(self, force_build: bool) -> None:
        self._root = Path(tempfile.mkdtemp(prefix=scratch.name("workspace") + "-"))
        await asyncio.to_thread(create_workspace, self._project, self._root)

    async def stop(self, delete: bool):
        if self._root is not None:
            shutil.rmtree(self._root, ignore_errors=True)
            self._root = None

    async def exec(self, command: str, cwd: str | None = None, env: dict[str, str] | None = None,
                   timeout_sec: int | None = None, user: str | int | None = None) -> ExecResult:
        root = str(self._root)
        variables = local_env(self._root / "app", self._root / "tests", self._root / "logs/verifier",
                              self._merge_env(env))
        command = self.PATTERN.sub(lambda m: root + "/" + m[1], command)
        workdir = self._host(cwd or self.task_env_config.workdir or "/app")
        return await _run(["bash", "-c", command], variables, timeout_sec, cwd=str(workdir))
