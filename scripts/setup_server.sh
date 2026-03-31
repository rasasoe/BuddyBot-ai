#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$ROOT_DIR/.venv"

cd "$ROOT_DIR"

python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo
echo "[setup] server environment ready"
echo "[setup] activate with:"
echo "  source $VENV_DIR/bin/activate"
echo "[setup] run with:"
echo "  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
