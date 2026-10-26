"""Check or provision user-owned tools; no system packages or shared binaries are replaced."""
import argparse
import hashlib
import importlib.util
import json
import os
import platform
import re
import shutil
import struct
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / '.tools'
GH_VERSION = '2.103.2'
GH_ROUTER = '''#!/bin/sh
# CS408: one portable launcher, independent binaries for each machine.
LAB2_TOOLS=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
case "$(uname -s):$(uname -m)" in
  Linux:aarch64|Linux:arm64) LAB2_GH_PLATFORM=linux-arm64 ;;
  Linux:x86_64|Linux:amd64) LAB2_GH_PLATFORM=linux-amd64 ;;
  *) echo "gh: unsupported platform" >&2; exit 126 ;;
esac
LAB2_GH="$LAB2_TOOLS/gh/$LAB2_GH_PLATFORM/bin/gh"
if [ ! -x "$LAB2_GH" ]; then
  echo "gh: missing $LAB2_GH; run bash setup.sh on this machine" >&2; exit 127
fi
exec "$LAB2_GH" "$@"
'''


def machine():
    arch = {'arm64': 'aarch64', 'amd64': 'x86_64'}.get(platform.machine().lower(), platform.machine().lower())
    if platform.system() != 'Linux' or arch not in ['aarch64', 'x86_64']:
        raise RuntimeError('Use Linux ARM64, or Linux x86_64 for Warmup only.')
    return 'linux-arm64' if arch == 'aarch64' else 'linux-amd64'


def works(command, env=None):
    try:
        result = subprocess.run([str(x) for x in command], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                env=env, timeout=20, text=True)
        return result.returncode == 0, result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return False, ''


def execute(command, env=None):
    print('+', ' '.join(map(str, command)), flush=True)
    subprocess.run([str(x) for x in command], env=env, check=True)


def download(url, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={'User-Agent': 'cs408-lab2-setup'})
    with urllib.request.urlopen(request, timeout=90) as response, path.open('wb') as target:
        shutil.copyfileobj(response, target)


def extract_binary(archive, member, destination):
    with tarfile.open(archive, 'r:*') as bundle:
        entry = bundle.getmember(member)
        if not entry.isfile():
            raise RuntimeError('Expected a regular binary in the release archive')
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix('.installing')
        with bundle.extractfile(entry) as source, temporary.open('wb') as target:
            shutil.copyfileobj(source, target)
        temporary.chmod(0o755)
        temporary.replace(destination)


def elf_machine(path):
    with path.open('rb') as file:
        header = file.read(20)
    if header[:4] != b'\x7fELF' or len(header) != 20:
        raise RuntimeError('Downloaded executable is not ELF')
    return struct.unpack('<H' if header[5] == 1 else '>H', header[18:20])[0]


def install_gh(current):
    destination = TOOLS / 'gh' / current / 'bin/gh'
    expected = 183 if current == 'linux-arm64' else 62
    if not (destination.is_file() and elf_machine(destination) == expected and works([destination, '--version'])[0]):
        suffix = 'arm64' if current == 'linux-arm64' else 'amd64'
        filename = 'gh_{}_linux_{}.tar.gz'.format(GH_VERSION, suffix)
        url = 'https://github.com/cli/cli/releases/download/v' + GH_VERSION + '/'
        with tempfile.TemporaryDirectory(prefix='lab2-gh-') as directory:
            archive, checksums = Path(directory) / filename, Path(directory) / 'checksums.txt'
            download(url + filename, archive)
            download(url + 'gh_{}_checksums.txt'.format(GH_VERSION), checksums)
            expected_hash = next((line.split()[0] for line in checksums.read_text().splitlines()
                                  if line.split()[-1].lstrip('*') == filename), None)
            if expected_hash is None or hashlib.sha256(archive.read_bytes()).hexdigest() != expected_hash:
                raise RuntimeError('GitHub CLI checksum mismatch')
            extract_binary(archive, 'gh_{}_linux_{}/bin/gh'.format(GH_VERSION, suffix), destination)
            if elf_machine(destination) != expected:
                raise RuntimeError('GitHub CLI architecture mismatch')
    launcher = TOOLS / 'bin/gh'
    launcher.parent.mkdir(parents=True, exist_ok=True)
    launcher.write_text(GH_ROUTER)
    launcher.chmod(0o755)


def install_git(current, env):
    required = {'git': 'git', 'curl': 'curl', 'tar': 'tar', 'find': 'findutils',
                'chmod': 'coreutils', 'chgrp': 'coreutils'}
    missing = sorted({package for tool, package in required.items()
                      if not shutil.which(tool, path=env.get('PATH'))})
    if not missing:
        return
    suffix = 'linux-aarch64' if current == 'linux-arm64' else 'linux-64'
    binary = TOOLS / 'micromamba' / current / 'micromamba'
    if not binary.exists():
        with tempfile.TemporaryDirectory(prefix='lab2-mamba-') as directory:
            archive = Path(directory) / 'micromamba.tar.bz2'
            download('https://micro.mamba.pm/api/micromamba/' + suffix + '/latest', archive)
            extract_binary(archive, 'bin/micromamba', binary)
    env = dict(env, MAMBA_ROOT_PREFIX=str(TOOLS / 'mamba' / current))
    execute([binary, '--no-rc', 'create', '-y', '-c', 'conda-forge', '--override-channels',
             '-p', TOOLS / 'git' / current, *missing], env)


def upstream(env):
    destination = ROOT / 'vendor/mini-swe-agent'
    config = (ROOT / 'pyproject.toml').read_text()
    commit = re.search(r'^commit = "([a-f0-9]{40})"$', config, re.M).group(1)
    if not (destination / 'pyproject.toml').exists():
        ok, top = works(['git', '-C', ROOT, 'rev-parse', '--show-toplevel'], env)
        if ok:
            relative = str(destination.relative_to(Path(top)))
            subprocess.run(['git', '-C', top, 'submodule', 'update', '--init', '--recursive', '--', relative], env=env)
        if not (destination / 'pyproject.toml').exists():
            execute(['git', 'clone', 'https://github.com/SWE-agent/mini-swe-agent.git', destination], env)
    ok, head = works(['git', '-C', destination, 'rev-parse', 'HEAD'], env)
    if not ok:
        raise RuntimeError('The mini-swe-agent submodule is not a Git checkout')
    if head != commit:
        _, dirty = works(['git', '-C', destination, 'status', '--porcelain'], env)
        if dirty:
            raise RuntimeError('mini-swe-agent has local edits; setup will not overwrite them')
        execute(['git', '-C', destination, 'checkout', '--detach', commit], env)


def status(current, env):
    python = ROOT / '.venvs' / current / 'bin/python'
    checks = {}
    for name, command in [('git', ['git', '--version']), ('gh', ['gh', '--version']),
                          ('Python', [python, '--version'])]:
        ok, text = works(command, env)
        checks[name] = {'ok': ok, 'detail': text.splitlines()[0] if ok and text else 'not available'}
    for tool in ['curl', 'tar', 'find', 'chmod', 'chgrp']:
        checks[tool] = {'ok': bool(shutil.which(tool, path=env.get('PATH'))), 'detail': 'user-space or system executable'}
    packages = works([python, '-c', 'import adapter, lab2, minisweagent, openai, pytest, udocker'], env)[0]
    engines = TOOLS / 'udocker' / current / 'bin'
    checks['Python packages'] = {'ok': packages, 'detail': 'adapter, mini-swe-agent, OpenAI SDK, pytest, udocker'}
    checks['udocker engines'] = {'ok': engines.is_dir() and any(engines.iterdir()), 'detail': str(engines)}
    key = bool(env.get('PURDUE_RCAC_API_KEY'))
    checks['Purdue API key'] = {'ok': key, 'detail': 'set (value never printed)' if key else 'not set; required for agent runs'}
    auth = works(['gh', 'auth', 'status', '--hostname', 'github.com'], env)[0] if checks['gh']['ok'] else False
    print('\nMachine: {}. Benchmark images: {}.'.format(current, 'supported' if current == 'linux-arm64' else 'ARM64 required; Warmup only'))
    for name, check in checks.items():
        print('{:<18} {:<7} {}'.format(name, 'OK' if check['ok'] else 'MISSING', check['detail']))
    print('GitHub login: {} (optional for public images and source).'.format('available' if auth else 'not available'))
    return {'platform': current, 'arm64_benchmarks_supported': current == 'linux-arm64',
            'checks': checks, 'github_authenticated': auth,
            'dependencies_ready': all(checks[k]['ok'] for k in ['git', 'gh', 'Python', 'Python packages', 'udocker engines', 'curl', 'tar', 'find', 'chmod', 'chgrp']),
            'api_key_present': key}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check only; do not install or change files')
    args = parser.parse_args()
    current = machine()
    python = ROOT / '.venvs' / current / 'bin/python'
    env = dict(os.environ, **{'PATH': os.pathsep.join([str(TOOLS / 'bin'), str(TOOLS / 'git' / current / 'bin'),
                                               str(python.parent), os.environ.get('PATH', '')]),
                        'UDOCKER_DIR': str(TOOLS / 'udocker' / current)})
    if not args.check:
        install_git(current, env)
        upstream(env)
        uv = TOOLS / 'uv' / current / 'uv'
        if not python.exists():
            execute([uv, 'venv', '--python', sys.executable, python.parent.parent], env)
        execute([uv, 'pip', 'install', '--python', python, '-e', ROOT / 'vendor/mini-swe-agent',
                 '-e', str(ROOT) + '[test,docs]'], env)
        install_gh(current)
        execute([python.parent / 'udocker', 'install'], env)
    report = status(current, env)
    if not args.check:
        destination = TOOLS / 'status' / (current + '.json')
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(report, indent=2) + '\n')
        print('\nActivate: source scripts/activate.sh')
    return 0 if report['dependencies_ready'] else 1


if __name__ == '__main__':
    sys.exit(main())
