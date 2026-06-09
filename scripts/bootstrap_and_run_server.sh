#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -d .git ]; then
  echo "Error: not a git repository: $ROOT_DIR"
  exit 1
fi

CURRENT_BRANCH="$(git symbolic-ref --short HEAD)"
STATUS="$(git status --porcelain)"
BACKUP_BRANCH="backup/server-local-$(date +%Y%m%d-%H%M%S)"

if [ -n "$STATUS" ]; then
  echo "Local changes detected. Creating backup branch: $BACKUP_BRANCH"
  git switch -c "$BACKUP_BRANCH"
  git add -A
  git commit -m "Backup server local changes before hybrid STT sync"
  echo "Backup commit created on branch $BACKUP_BRANCH"
  git switch "$CURRENT_BRANCH"
else
  echo "No local changes detected. Skipping backup branch creation."
fi

if [ "$CURRENT_BRANCH" != "main" ]; then
  echo "Switching to main branch"
  git switch main
fi

echo "Pulling latest origin/main"
git pull --ff-only origin main

bash scripts/setup_server.sh

ENV_FILE="$ROOT_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
  cat > "$ENV_FILE" <<'EOF'
STT_MODEL_SIZE=large-v3-turbo
STT_DEVICE=cuda
STT_COMPUTE_TYPE=float16
STT_LANGUAGE=ko
EOF
  if [ -d "$ROOT_DIR/../BuddyBot" ]; then
    echo "BUDDYBOT_REPO_PATH=../BuddyBot" >> "$ENV_FILE"
  fi
  echo "Created .env with recommended STT settings."
else
  echo ".env already exists. Leaving existing file intact."
fi

if [ -f "$ROOT_DIR/.venv/bin/activate" ]; then
  source "$ROOT_DIR/.venv/bin/activate"
elif [ -f "$ROOT_DIR/venv/bin/activate" ]; then
  source "$ROOT_DIR/venv/bin/activate"
else
  echo "Error: virtual environment not found after setup."
  exit 1
fi

echo "Starting BuddyBot-ai server..."
UVICORN_ARGS=(app.main:app --host 0.0.0.0 --port "${PORT:-8000}")
if [ "${BUDDYBOT_AI_RELOAD:-0}" = "1" ]; then
  UVICORN_ARGS+=(--reload)
fi
exec python -m uvicorn "${UVICORN_ARGS[@]}"
