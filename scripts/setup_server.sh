#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$ROOT_DIR/.venv"

cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON:-python3}"
if [ -d "$VENV_DIR" ] && [ ! -x "$VENV_DIR/bin/python" ]; then
  BROKEN_VENV="${VENV_DIR}.broken-$(date +%Y%m%d-%H%M%S)"
  echo "[setup] broken venv detected; moving $VENV_DIR to $BROKEN_VENV"
  mv "$VENV_DIR" "$BROKEN_VENV"
fi

"$PYTHON_BIN" -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo
echo "[setup] server environment ready"
echo "[setup] activate with:"
echo "  source $VENV_DIR/bin/activate"
echo "[setup] run with:"
echo "  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
