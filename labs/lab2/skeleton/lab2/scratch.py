"""Names of the temporary containers and folders lab2 creates, and their cleanup.

    from lab2 import scratch
    name = scratch.name("eval")      # lab2-eval-<pid>-<random>
    scratch.clean()                  # remove leftovers of processes that no longer run

Every udocker container and temporary folder carries the id of the process that
created it. They are removed when that process finishes normally; a process that
was killed (kill -9, out of memory, closed session) leaves them behind, each
container holding about 100k files. clean() removes exactly those leftovers:
names in this format whose process is gone. Anything else, including the
scratch of processes still running, is left alone. It also removes images
pulled into the user's store once no lab2 command of the user runs
(lab2.environments.own_images). `run`, `eval` and grading/eval.py call it
before they start.
"""
import os
import re
import shutil
import tempfile
import uuid
from pathlib import Path

# lab2-<kind>-<pid>-<random>, plus the suffix tempfile adds to temporary folder names
PATTERN = re.compile(r"^lab2-[a-z]+-(\d+)-[0-9a-f]{8}(-[a-z0-9_]+)?$")


def name(kind: str) -> str:
    """A fresh scratch name owned by this process, e.g. lab2-eval-4711-1a2b3c4d."""
    return f"lab2-{kind}-{os.getpid()}-{uuid.uuid4().hex[:8]}"


def temporary_directory(kind: str) -> tempfile.TemporaryDirectory:
    """A temporary folder named like name(kind) (with a random suffix added by tempfile)."""
    return tempfile.TemporaryDirectory(prefix=name(kind) + "-")


def owner_gone(entry: str) -> bool:
    """True if `entry` is lab2 scratch whose creating process no longer runs."""
    match = PATTERN.match(entry)
    if not match:
        return False
    try:
        os.kill(int(match.group(1)), 0)
    except ProcessLookupError:
        return True
    except PermissionError:  # a process of another user has this id: keep the entry
        return False
    return False


def clean(store: Path | None = None) -> list[str]:
    """Remove leftover containers, command markers and pulled images from the
    image store, and leftover temporary folders."""
    from lab2.environments import Udocker, normalize_tree, remove_own_images

    removed = []
    udocker = Udocker(store)
    containers = udocker.store / "containers"
    if containers.is_dir():
        for alias in containers.iterdir():
            if alias.is_symlink() and owner_gone(alias.name):
                udocker.remove(alias.name)
                removed.append(str(alias))
    for marker in udocker.store.glob("lab2-command-*"):
        if owner_gone(marker.name):
            marker.unlink(missing_ok=True)
            removed.append(str(marker))
    if (udocker.store / "layers").is_dir() and remove_own_images(udocker.store):
        removed.append(str(udocker.store / "layers"))
    for folder in Path(tempfile.gettempdir()).glob("lab2-*"):
        if folder.is_dir() and not folder.is_symlink() and owner_gone(folder.name):
            normalize_tree(folder)  # udocker trees may lack owner write permission
            shutil.rmtree(folder, ignore_errors=True)
            removed.append(str(folder))
    return removed
