"""Shared fixtures: a fake model endpoint and a throw-away lab (tasks/, jobs/, skills/).

No test calls the Purdue API; model requests go to a local HTTP server that
replays queued Chat Completions replies.
"""
import difflib
import json
import subprocess
import tempfile
import threading
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
import yaml

from lab2 import jobs, skills, tasks
from lab2.environments import create_workspace


def completion(arguments, cached=None):
    """A Chat Completions reply with one bash tool call and full usage."""
    return {"id": "test-response", "object": "chat.completion", "created": 0, "model": "qwen3.8:27b",
            "choices": [{"index": 0, "finish_reason": "tool_calls", "message": {
                "role": "assistant", "content": "", "tool_calls": [{
                    "id": "call-1", "type": "function", "function": {"name": "bash", "arguments": arguments}}]}}],
            "usage": {"prompt_tokens": 1000, "completion_tokens": 200, "total_tokens": 1200,
                      "completion_tokens_details": {"reasoning_tokens": 150},
                      "prompt_tokens_details": None if cached is None else {"cached_tokens": cached}}}


def command(text):
    return 200, completion(json.dumps({"command": text}))


@pytest.fixture
def endpoint(monkeypatch):
    """(url, replies, requests): queue (status, body) replies; requests records the bodies."""
    monkeypatch.setenv("LAB2_TEST_KEY", "test-only")
    replies, requests = deque(), []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            requests.append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
            status, reply = replies.popleft()
            body = json.dumps(reply).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/api", replies, requests
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def patch(name, old, new):
    """Unified diff turning file `name` from `old` into `new` (git apply format)."""
    return "".join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), "a/" + name, "b/" + name))


CALC = "def double(x):\n    return 2 * x\n\n\ndef sign(x):\n    if x < 0:\n        return -1\n    return 1\n"
STARTER = "from calc import double\n\n\ndef test_double():\n    assert double(2) == 4\n"


def workspace_head(project):
    """The (deterministic) commit of a local workspace made from `project`."""
    with tempfile.TemporaryDirectory() as tmp:
        app = create_workspace(project, Path(tmp) / "workspace") / "app"
        return subprocess.run(["git", "-C", str(app), "rev-parse", "HEAD"], capture_output=True, text=True,
                              check=True).stdout.strip()


def write_task(root, task_id="calc", kind="warmup", calc=CALC, **spec):
    """A local python task with two checkpoints (double: one faulty version, sign: two).

    calc: the project's calc.py (faulty versions always patch CALC).
    """
    folder = root / "tasks" / kind / task_id
    (folder / "project").mkdir(parents=True)
    (folder / "project" / "calc.py").write_text(calc)
    (folder / "project" / "test_calc.py").write_text(STARTER)
    (folder / "prompt.md").write_text("Write tests for calc.py.\n")
    base = {"id": task_id, "type": kind, "language": "python", "prompt": "prompt.md", "test_paths": ["."],
            "editable": ["test_calc.py"],
            "environment": {"local": True, "project": "project", "head": workspace_head(folder / "project")}}
    (folder / "task.yaml").write_text(yaml.safe_dump({**base, **spec}))
    checkpoints = [
        {"id": "double", "label": "double doubles", "hidden": False, "faulty_versions": [
            {"id": "double-adds", "patch": patch("calc.py", CALC, CALC.replace("2 * x", "x + 2"))}]},
        {"id": "sign", "label": "sign of negatives and zero", "hidden": True,
         "faulty_versions": [
             {"id": "sign-le", "patch": patch("calc.py", CALC, CALC.replace("x < 0", "x <= 0"))},
             {"id": "sign-flipped", "patch": patch("calc.py", CALC, CALC.replace("return -1", "return 1"))}]}]
    (folder / "checkpoints.json").write_text(json.dumps({"task": task_id, "checkpoints": checkpoints}))
    return folder


@pytest.fixture
def lab(tmp_path, monkeypatch):
    """Temporary jobs/, skills/ and tasks/ with one made-up warmup task `calc`."""
    monkeypatch.setattr(jobs, "JOBS_DIR", tmp_path / "jobs")
    monkeypatch.setattr(skills, "SKILLS_DIR", tmp_path / "skills")
    monkeypatch.setattr(tasks, "TASKS_DIR", tmp_path / "tasks")
    (tmp_path / "skills").mkdir()
    write_task(tmp_path)
    return tmp_path


def write_skill(lab, name, description="Fixture skill.", body="Read references/probe.txt when needed.\n"):
    folder = lab / "skills" / name
    (folder / "references").mkdir(parents=True)
    (folder / "SKILL.md").write_text(f"---\nname: {name}\ndescription: {description}\n---\n\n{body}")
    (folder / "references" / "probe.txt").write_text("Supplementary fixture.\n")
    return folder
