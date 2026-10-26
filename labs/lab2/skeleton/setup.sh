#!/usr/bin/env bash
# Bootstrap a native Python without changing the system or shell profiles.
set -euo pipefail
LAB2_ROOT=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
case "$(uname -s):$(uname -m)" in
  Linux:aarch64|Linux:arm64) LAB2_PLATFORM=linux-arm64 ;;
  Linux:x86_64|Linux:amd64) LAB2_PLATFORM=linux-amd64 ;;
  *) echo 'This lab needs Linux ARM64 (benchmarks) or Linux x86_64 (Warmup only).' >&2; exit 1 ;;
esac
LAB2_UV="$LAB2_ROOT/.tools/uv/$LAB2_PLATFORM/uv"
if [[ "${1:-}" == --check || "${1:-}" == --help || "${1:-}" == -h ]]; then
  if [[ -x "$LAB2_ROOT/.venvs/$LAB2_PLATFORM/bin/python" ]]; then
    exec "$LAB2_ROOT/.venvs/$LAB2_PLATFORM/bin/python" "$LAB2_ROOT/scripts/setup.py" "$@"
  fi
  if command -v python3 >/dev/null && python3 -c 'import sys; assert sys.version_info >= (3, 8)' 2>/dev/null; then
    exec python3 "$LAB2_ROOT/scripts/setup.py" "$@"
  fi
  echo "Machine: $LAB2_PLATFORM. Python 3.8+ not found; run bash setup.sh to bootstrap Python 3.12." >&2
  exit 1
fi
if [[ ! -x "$LAB2_UV" ]]; then
  LAB2_INSTALLER=$(mktemp)
  trap 'rm -f "$LAB2_INSTALLER"' EXIT
  if command -v curl >/dev/null; then
    curl --fail --location --silent --show-error https://astral.sh/uv/install.sh -o "$LAB2_INSTALLER"
  elif command -v wget >/dev/null; then
    wget -q https://astral.sh/uv/install.sh -O "$LAB2_INSTALLER"
  elif command -v python3 >/dev/null; then
    python3 -c 'import sys,urllib.request; urllib.request.urlretrieve(sys.argv[1],sys.argv[2])' https://astral.sh/uv/install.sh "$LAB2_INSTALLER"
  else
    echo 'Bootstrap needs curl, wget, or Python 3 to download uv.' >&2; exit 1
  fi
  env UV_UNMANAGED_INSTALL="$LAB2_ROOT/.tools/uv/$LAB2_PLATFORM" sh "$LAB2_INSTALLER"
  rm -f "$LAB2_INSTALLER"
  trap - EXIT
fi
export UV_PYTHON_INSTALL_DIR="$LAB2_ROOT/.tools/python/$LAB2_PLATFORM"
export UV_PYTHON_BIN_DIR="$LAB2_ROOT/.tools/python-bin/$LAB2_PLATFORM"
export UV_CACHE_DIR="$LAB2_ROOT/.cache/uv/$LAB2_PLATFORM"
"$LAB2_UV" python install 3.12
LAB2_PYTHON=$("$LAB2_UV" python find --managed-python 3.12)
exec "$LAB2_PYTHON" "$LAB2_ROOT/scripts/setup.py" "$@"
