#!/usr/bin/env bash
set -euo pipefail
VENV_DIR="${VENV_DIR:-.venv}"
if [ ! -d "$VENV_DIR" ]; then
  echo "[*] No venv found, bootstrapping..."
  bash setup_venv.sh
fi
exec "$VENV_DIR/bin/llm-arena" "$@"
