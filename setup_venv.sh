#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3.12}"
VENV_DIR="${VENV_DIR:-.venv}"

echo "[*] Using Python: $PYTHON_BIN"
$PYTHON_BIN -V

if [ ! -d "$VENV_DIR" ]; then
  echo "[*] Creating venv at $VENV_DIR"
  $PYTHON_BIN -m venv "$VENV_DIR"
fi

echo "[*] Upgrading pip/setuptools/wheel"
"$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel

echo "[*] Installing project in editable mode"
"$VENV_DIR/bin/python" -m pip install -e .

echo
echo "[*] Done. Activate with:"
echo "    source $VENV_DIR/bin/activate"
echo
echo "[*] Example run:"
echo "    $VENV_DIR/bin/llm-arena --prompt 'Erkläre TCP in drei Sätzen' --reveal-provenance false"
