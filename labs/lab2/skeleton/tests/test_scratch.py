"""Scratch names and the cleanup of leftovers from killed processes."""
import os
import re
import subprocess
import tempfile

from lab2 import scratch


def dead_pid() -> int:
    """The id of a process that has already exited."""
    p = subprocess.Popen(["true"])
    p.wait()
    return p.pid


def test_names_carry_the_process_id():
    assert re.fullmatch(rf"lab2-eval-{os.getpid()}-[0-9a-f]{{8}}", scratch.name("eval"))
    with scratch.temporary_directory("run") as folder:
        assert scratch.PATTERN.match(os.path.basename(folder))
        assert not scratch.owner_gone(os.path.basename(folder))  # this process still runs


def test_clean_removes_only_leftovers_of_finished_processes(tmp_path, monkeypatch):
    temp, store = tmp_path / "tmp", tmp_path / "store"
    temp.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(temp))
    dead, alive = dead_pid(), os.getpid()
    for folder in [f"lab2-run-{dead}-0011aabb-x1y2", f"lab2-run-{alive}-0011aabb-x1y2", "lab2-other", "unrelated"]:
        (temp / folder).mkdir()
    containers = store / "containers"
    for name in [f"lab2-eval-{dead}-aabbccdd", f"lab2-eval-{alive}-aabbccdd", "lab2-eval-oldstyle"]:
        (containers / (name + "-id") / "ROOT").mkdir(parents=True)
        (containers / name).symlink_to(name + "-id")

    removed = scratch.clean(store)

    assert sorted(p.name for p in temp.iterdir()) == ["lab2-other", f"lab2-run-{alive}-0011aabb-x1y2", "unrelated"]
    assert sorted(p.name for p in containers.iterdir()) == sorted(
        [f"lab2-eval-{alive}-aabbccdd", f"lab2-eval-{alive}-aabbccdd-id", "lab2-eval-oldstyle", "lab2-eval-oldstyle-id"])
    assert len(removed) == 2
