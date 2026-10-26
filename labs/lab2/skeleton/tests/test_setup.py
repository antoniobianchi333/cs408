"""Installation boundaries that matter on a shared ARM/x86 home directory."""
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import tarfile

import pytest

spec = importlib.util.spec_from_file_location('lab_setup', Path(__file__).parents[1] / 'scripts/setup.py')
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


def executable(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    path.chmod(0o755)


@pytest.mark.parametrize('arch,slot', [('aarch64', 'linux-arm64'), ('x86_64', 'linux-amd64')])
def test_router_selects_machine_and_preserves_arguments(tmp_path, arch, slot):
    tools = tmp_path / 'tools'
    executable(tools / 'bin/gh', setup.GH_ROUTER)
    for platform in ['linux-arm64', 'linux-amd64']:
        executable(tools / 'gh' / platform / 'bin/gh', '#!/bin/sh\nprintf "%s\\n" ' + platform + ' "$@"\n')
    executable(tmp_path / 'bin/uname', '#!/bin/sh\ncase "$1" in -s) echo Linux;; -m) echo ' + arch + ';; esac\n')
    env = dict(os.environ, PATH=str(tmp_path / 'bin') + ':' + os.environ['PATH'])
    result = subprocess.run([tools / 'bin/gh', 'two words', '*.txt'], env=env, capture_output=True, text=True, check=True)
    assert result.stdout.splitlines() == [slot, 'two words', '*.txt']
    (tools / 'gh' / slot / 'bin/gh').unlink()
    assert subprocess.run([tools / 'bin/gh'], env=env, capture_output=True).returncode == 127


def test_checksum_failure_does_not_touch_other_architecture(tmp_path, monkeypatch):
    monkeypatch.setattr(setup, 'TOOLS', tmp_path)
    other = tmp_path / 'gh/linux-amd64/bin/gh'
    executable(other, 'existing x86 installation')
    def download(url, destination):
        destination.write_bytes(b'incorrect archive' if url.endswith('.tar.gz') else b'0 gh_2.103.2_linux_arm64.tar.gz\n')
    monkeypatch.setattr(setup, 'download', download)
    with pytest.raises(RuntimeError, match='checksum mismatch'):
        setup.install_gh('linux-arm64')
    assert other.read_text() == 'existing x86 installation'
    assert not (tmp_path / 'bin/gh').exists()


def test_archive_only_extracts_requested_regular_file(tmp_path):
    archive = tmp_path / 'release.tar'
    with tarfile.open(archive, 'w') as tar:
        bad = tarfile.TarInfo('../../escape')
        bad.size = 3
        tar.addfile(bad, io.BytesIO(b'bad'))
        link = tarfile.TarInfo('bin/gh')
        link.type = tarfile.SYMTYPE
        link.linkname = '/etc/passwd'
        tar.addfile(link)
    with pytest.raises(RuntimeError, match='regular binary'):
        setup.extract_binary(archive, 'bin/gh', tmp_path / 'installed/gh')
    assert not (tmp_path / 'installed').exists()
