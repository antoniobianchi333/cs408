"""scripts/setup.py: safe archive extraction, how the vendored packages are installed, tectonic status."""
import importlib.util
import io
import sys
import tarfile
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("lab_setup", Path(__file__).parents[1] / "scripts/setup.py")
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


def test_archive_only_extracts_requested_regular_file(tmp_path):
    archive = tmp_path / "release.tar"
    with tarfile.open(archive, "w") as tar:
        bad = tarfile.TarInfo("../../escape")
        bad.size = 3
        tar.addfile(bad, io.BytesIO(b"bad"))
        link = tarfile.TarInfo("bin/micromamba")
        link.type = tarfile.SYMTYPE
        link.linkname = "/etc/passwd"
        tar.addfile(link)
    with pytest.raises(RuntimeError, match="regular binary"):
        setup.extract_binary(archive, "bin/micromamba", tmp_path / "installed/micromamba")
    assert not (tmp_path / "installed").exists()


def test_vendored_packages_are_installed_from_copies(tmp_path, monkeypatch):
    """Not editable, and mini-swe-agent is built from a temporary copy (no egg-info in vendor/)."""
    commands = []

    def execute(command, env=None):
        command = [str(c) for c in command]
        if "pip" in command:
            mini = Path(next(c for c in command if c.endswith("/mini-swe-agent")))
            assert setup.ROOT not in mini.parents and (mini / "pyproject.toml").is_file()
            assert not (mini / ".git").exists() and not list(mini.glob("src/*.egg-info"))
        commands.append(command)

    monkeypatch.setattr(setup, "TOOLS", tmp_path)
    monkeypatch.setattr(setup, "execute", execute)
    for name in ("install_git", "install_tectonic", "vendor"):
        monkeypatch.setattr(setup, name, lambda *args: None)
    monkeypatch.setattr(setup, "harbor_supported", lambda python: True)
    monkeypatch.setattr(setup, "status", lambda current, env: {"dependencies_ready": True})
    monkeypatch.setattr(sys, "argv", ["setup.py"])
    assert setup.main() == 0
    [pip] = [c for c in commands if "pip" in c]
    assert "-e" not in pip and str(setup.ROOT / "vendor/harbor") in pip and "--no-cache" in pip


def test_status_requires_tectonic(tmp_path, monkeypatch):
    """The user-space tectonic is reported and counts as a dependency."""
    monkeypatch.setattr(setup, "TOOLS", tmp_path)
    missing = setup.status("linux-arm64", {"PATH": ""})
    assert missing["checks"]["tectonic"] == {"ok": False, "detail": "not available"}
    assert not missing["dependencies_ready"]
    binary = tmp_path / "tectonic/linux-arm64/tectonic"
    binary.parent.mkdir(parents=True)
    binary.write_text("#!/bin/sh\necho Tectonic 0.17.0\n")
    binary.chmod(0o755)
    assert setup.status("linux-arm64", {"PATH": ""})["checks"]["tectonic"] == {"ok": True, "detail": "Tectonic 0.17.0"}
