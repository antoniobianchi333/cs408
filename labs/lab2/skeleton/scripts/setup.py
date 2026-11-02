"""Install or check the Lab 2 tools; nothing outside the repository is changed.

    bash setup.sh            install (run through setup.sh, which provides Python 3.12)
    bash setup.sh --check    report only

Installs git/curl/... via micromamba when missing, checks out the vendored
mini-swe-agent and Harbor at the commits pinned in pyproject.toml, creates a
venv under .venvs/<platform>/ with the requirements of pyproject.toml and the
two vendored packages (uv, without a package cache; installed as copies, not
editable, so nothing is generated inside vendor/), installs the udocker
engines, and installs tectonic (LaTeX, for report/) under .tools/tectonic/<platform>/.
Harbor needs Python >= 3.12.
"""
import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / ".tools"
REQUIRED = ["git", "Python", "Python packages", "udocker engines", "tectonic", "curl", "tar", "find", "chmod", "chgrp"]
TECTONIC = "0.17.0"


def machine():
    arch = {"arm64": "aarch64", "amd64": "x86_64"}.get(platform.machine().lower(), platform.machine().lower())
    if platform.system() != "Linux" or arch not in ["aarch64", "x86_64"]:
        raise RuntimeError("Use Linux ARM64, or Linux x86_64 for Warmup only.")
    return "linux-arm64" if arch == "aarch64" else "linux-amd64"


def works(command, env=None):
    """(succeeded, output) of a short command; never raises."""
    try:
        result = subprocess.run([str(x) for x in command], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                env=env, timeout=20, text=True)
        return result.returncode == 0, result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return False, ""


def execute(command, env=None):
    print("+", " ".join(map(str, command)), flush=True)
    subprocess.run([str(x) for x in command], env=env, check=True)


def download(url, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "cs408-lab2-setup"})
    with urllib.request.urlopen(request, timeout=90) as response, path.open("wb") as target:
        shutil.copyfileobj(response, target)


def extract_binary(archive, member, destination):
    """Extract one regular file from a tar archive (nothing else, no links)."""
    with tarfile.open(archive, "r:*") as bundle:
        entry = bundle.getmember(member)
        if not entry.isfile():
            raise RuntimeError("Expected a regular binary in the release archive")
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(".installing")
        with bundle.extractfile(entry) as source, temporary.open("wb") as target:
            shutil.copyfileobj(source, target)
        temporary.chmod(0o755)
        temporary.replace(destination)


def install_git(current, env):
    """git, curl and basic tools from conda-forge (micromamba) when the system lacks them."""
    required = {"git": "git", "curl": "curl", "tar": "tar", "find": "findutils",
                "chmod": "coreutils", "chgrp": "coreutils"}
    missing = sorted({package for tool, package in required.items()
                      if not shutil.which(tool, path=env.get("PATH"))})
    if not missing:
        return
    suffix = "linux-aarch64" if current == "linux-arm64" else "linux-64"
    binary = TOOLS / "micromamba" / current / "micromamba"
    if not binary.exists():
        with tempfile.TemporaryDirectory(prefix="lab2-mamba-") as directory:
            archive = Path(directory) / "micromamba.tar.bz2"
            download(f"https://micro.mamba.pm/api/micromamba/{suffix}/latest", archive)
            extract_binary(archive, "bin/micromamba", binary)
    env = dict(env, MAMBA_ROOT_PREFIX=str(TOOLS / "mamba" / current))
    execute([binary, "--no-rc", "create", "-y", "-c", "conda-forge", "--override-channels",
             "-p", TOOLS / "git" / current, *missing], env)


def install_tectonic(current):
    """tectonic (self-contained LaTeX engine) from its GitHub release; builds report/main.pdf."""
    binary = TOOLS / "tectonic" / current / "tectonic"
    if not binary.exists():
        arch = "aarch64" if current == "linux-arm64" else "x86_64"
        release = f"https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%40{TECTONIC}"
        with tempfile.TemporaryDirectory(prefix="lab2-tectonic-") as directory:
            archive = Path(directory) / "tectonic.tar.gz"
            download(f"{release}/tectonic-{TECTONIC}-{arch}-unknown-linux-musl.tar.gz", archive)
            extract_binary(archive, "tectonic", binary)
    if not works([binary, "--version"])[0]:
        raise RuntimeError(f"{binary} does not run")


def vendor(env, name):
    """Check out vendor/<name> at the commit pinned in pyproject.toml [tool.cs408.vendor.<name>]."""
    destination = ROOT / "vendor" / name
    config = (ROOT / "pyproject.toml").read_text()
    block = config[config.index(f"[tool.cs408.vendor.{name}]"):]
    url = re.search(r'^repository = "(.+)"$', block, re.M).group(1) + ".git"
    commit = re.search(r'^commit = "([a-f0-9]{40})"$', block, re.M).group(1)
    if not (destination / "pyproject.toml").exists():
        ok, top = works(["git", "-C", ROOT, "rev-parse", "--show-toplevel"], env)
        if ok:
            relative = str(destination.relative_to(Path(top)))
            subprocess.run(["git", "-C", top, "submodule", "update", "--init", "--recursive", "--", relative], env=env)
        if not (destination / "pyproject.toml").exists():
            execute(["git", "clone", "--depth", "1", url, destination], env)
    ok, head = works(["git", "-C", destination, "rev-parse", "HEAD"], env)
    if not ok:
        raise RuntimeError(f"The {name} submodule is not a Git checkout")
    if head != commit:
        _, dirty = works(["git", "-C", destination, "status", "--porcelain"], env)
        if dirty:
            raise RuntimeError(f"{name} has local edits; setup will not overwrite them")
        if not works(["git", "-C", destination, "cat-file", "-e", f"{commit}^{{commit}}"], env)[0]:
            execute(["git", "-C", destination, "fetch", "--depth", "1", "origin", commit], env)
        execute(["git", "-C", destination, "checkout", "--detach", commit], env)


def harbor_supported(python):
    ok, text = works([python, "-c", "import sys; print(sys.version_info >= (3, 12))"])
    return ok and text.strip() == "True"


def status(current, env):
    """Print and return the state of every tool the lab needs."""
    python = ROOT / ".venvs" / current / "bin/python"
    checks = {}
    for name, command in [("git", ["git", "--version"]), ("Python", [python, "--version"]),
                          ("tectonic", [TOOLS / "tectonic" / current / "tectonic", "--version"])]:
        ok, text = works(command, env)
        checks[name] = {"ok": ok, "detail": text.splitlines()[0] if ok and text else "not available"}
    for tool in ["curl", "tar", "find", "chmod", "chgrp"]:
        checks[tool] = {"ok": bool(shutil.which(tool, path=env.get("PATH"))), "detail": "user-space or system executable"}
    packages = works([python, "-c", "import lab2, minisweagent, harbor, openai, pytest, udocker"],
                     dict(env, PYTHONPATH=str(ROOT)))[0]
    engines = TOOLS / "udocker" / current / "bin"
    checks["Python packages"] = {"ok": packages, "detail": "lab2, mini-swe-agent, Harbor, OpenAI SDK, pytest, udocker"}
    checks["udocker engines"] = {"ok": engines.is_dir() and any(engines.iterdir()), "detail": str(engines)}
    key = bool(env.get("PURDUE_RCAC_API_KEY"))
    checks["Purdue API key"] = {"ok": key, "detail": "set (value never printed)" if key else "not set; required for agent runs"}
    benchmarks = "supported" if current == "linux-arm64" else "ARM64 required; Warmup only"
    print(f"\nMachine: {current}. Benchmark images: {benchmarks}.")
    for name, check in checks.items():
        print(f"{name:<18} {'OK' if check['ok'] else 'MISSING':<7} {check['detail']}")
    return {"platform": current, "arm64_benchmarks_supported": current == "linux-arm64", "checks": checks,
            "dependencies_ready": all(checks[k]["ok"] for k in REQUIRED), "api_key_present": key}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check only; do not install or change files")
    args = parser.parse_args()
    current = machine()
    python = ROOT / ".venvs" / current / "bin/python"
    path = os.pathsep.join([str(TOOLS / "git" / current / "bin"), str(python.parent), os.environ.get("PATH", "")])
    env = dict(os.environ, PATH=path, UDOCKER_DIR=str(TOOLS / "udocker" / current),
               PYTHONDONTWRITEBYTECODE="1")  # no __pycache__ in the source tree
    if not args.check:
        install_git(current, env)
        install_tectonic(current)
        for name in ("mini-swe-agent", "harbor"):
            vendor(env, name)
        uv = TOOLS / "uv" / current / "uv"
        if not python.exists():
            execute([uv, "venv", "--no-cache", "--python", sys.executable, python.parent.parent], env)
        if not harbor_supported(python):
            raise RuntimeError("Harbor needs Python >= 3.12; run bash setup.sh, which installs it")
        # The vendored packages are installed as copies, not editable. setuptools writes egg-info and
        # build/ into the folder it builds from, so mini-swe-agent is built from a temporary copy.
        with tempfile.TemporaryDirectory(prefix="lab2-build-") as directory:
            mini = Path(directory) / "mini-swe-agent"
            shutil.copytree(ROOT / "vendor/mini-swe-agent", mini,
                            ignore=shutil.ignore_patterns(".git", "*.egg-info", "build"))
            execute([uv, "pip", "install", "--no-cache", "--python", python, mini, ROOT / "vendor/harbor",
                     "-r", ROOT / "pyproject.toml", "--all-extras"], env)
        execute([python.parent / "udocker", "install"], env)
    report = status(current, env)
    if not args.check:
        destination = TOOLS / "status" / f"{current}.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(report, indent=2) + "\n")
        print("\nActivate: source scripts/activate.sh")
    return 0 if report["dependencies_ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
