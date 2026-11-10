# Lab 2 shell environment. Use from Bash: source scripts/activate.sh
# Activates the venv, puts the user-space tools first on PATH and the repository root on
# PYTHONPATH (the lab2 package is used in place, not installed).
LAB2_ROOT=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
case "$(uname -s):$(uname -m)" in
  Linux:aarch64|Linux:arm64) LAB2_PLATFORM=linux-arm64 ;;
  Linux:x86_64|Linux:amd64) LAB2_PLATFORM=linux-amd64 ;;
  *) echo 'Unsupported machine; use Linux for this lab.' >&2; return 1 ;;
esac
if [[ ! -f "$LAB2_ROOT/.venvs/$LAB2_PLATFORM/bin/activate" ]]; then
  echo 'Run bash setup.sh first.' >&2; return 1
fi
source "$LAB2_ROOT/.venvs/$LAB2_PLATFORM/bin/activate"
export PATH="$LAB2_ROOT/.tools/tectonic/$LAB2_PLATFORM:$LAB2_ROOT/.tools/git/$LAB2_PLATFORM/bin:$PATH"
export TECTONIC_CACHE_DIR="$LAB2_ROOT/.cache/tectonic"  # LaTeX packages for report/
export PYTHONPATH="$LAB2_ROOT${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONDONTWRITEBYTECODE=1
export UDOCKER_DIR="$LAB2_ROOT/.tools/udocker/$LAB2_PLATFORM"
export UV_PYTHON_INSTALL_DIR="$LAB2_ROOT/.tools/python/$LAB2_PLATFORM"
export UV_PYTHON_BIN_DIR="$LAB2_ROOT/.tools/python-bin/$LAB2_PLATFORM"
export UV_NO_CACHE=1
