"""Task registry: the tasks under tasks/<type>/<id>/.

Each task folder holds task.yaml (id, type, language, test_paths, editable,
source, environment, prepare, check), prompt.md, the public checkpoints.json,
for issue reproduction the correct code as solution.patch, and for the warmup
the project/ it runs on.

    from lab2 import tasks
    task = tasks.load("paperless")      # Task(id, type, dir, spec)
    for task in tasks.all_tasks(): ...
"""
from dataclasses import dataclass
from pathlib import Path

import yaml

SKELETON = Path(__file__).resolve().parents[1]
TASKS_DIR = SKELETON / "tasks"
TYPES = ("warmup", "test-writing", "issue-reproduction")

# Go actions run offline with the module cache baked into the image and a
# bounded number of compile jobs; task.yaml env values take precedence.
GO_ENV = {"GOMAXPROCS": "4", "GOFLAGS": "-p=4 -mod=readonly", "GOPROXY": "off", "GOSUMDB": "off"}


@dataclass(frozen=True)
class Task:
    id: str
    type: str
    dir: Path
    spec: dict

    @property
    def local(self) -> bool:
        """True for the warmup, which runs on the host instead of an image."""
        return bool(self.spec["environment"].get("local"))

    @property
    def workdir(self) -> str:
        return self.spec["environment"].get("workdir", "/app")

    @property
    def env(self) -> dict[str, str]:
        base = GO_ENV if self.spec["language"] == "go" else {}
        return {**base, **{k: str(v) for k, v in (self.spec["environment"].get("env") or {}).items()}}

    @property
    def checkpoints(self) -> Path:
        """The public checkpoints.json."""
        return self.dir / "checkpoints.json"

    @property
    def solution(self) -> Path | None:
        """The reference repair applied before scoring issue reproduction, else None."""
        return self.dir / "solution.patch" if self.type == "issue-reproduction" else None

    def prompt(self) -> str:
        """The exact instruction given to the agent."""
        text = (self.dir / self.spec.get("prompt", "prompt.md")).read_text()
        return text + "\nAllowed test directories: " + ", ".join(self.spec["test_paths"]) + "\n"


def all_tasks() -> list[Task]:
    """Every task, ordered by type (warmup, test-writing, issue-reproduction) and id."""
    found = []
    for kind in TYPES:
        for path in sorted((TASKS_DIR / kind).glob("*/task.yaml")):
            spec = yaml.safe_load(path.read_text())
            if spec.get("id") != path.parent.name or spec.get("type") != kind:
                raise ValueError(f"{path}: id/type must match the folder {kind}/{path.parent.name}")
            found.append(Task(spec["id"], kind, path.parent, spec))
    return found


def load(task_id: str) -> Task:
    for task in all_tasks():
        if task.id == task_id:
            return task
    raise ValueError(f"unknown task {task_id!r}; known: {', '.join(t.id for t in all_tasks())}")
