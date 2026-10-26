# Source this file from Bash: source scripts/activate.sh
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
export PATH="$LAB2_ROOT/.tools/bin:$LAB2_ROOT/.tools/git/$LAB2_PLATFORM/bin:$PATH"
export UDOCKER_DIR="$LAB2_ROOT/.tools/udocker/$LAB2_PLATFORM"
export UV_PYTHON_INSTALL_DIR="$LAB2_ROOT/.tools/python/$LAB2_PLATFORM"
export UV_PYTHON_BIN_DIR="$LAB2_ROOT/.tools/python-bin/$LAB2_PLATFORM"
export UV_CACHE_DIR="$LAB2_ROOT/.cache/uv/$LAB2_PLATFORM"
