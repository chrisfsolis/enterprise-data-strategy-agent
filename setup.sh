#!/usr/bin/env sh
set -eu
printf 'Current directory: %s\n' "$(pwd)"
if [ ! -f pyproject.toml ]; then
  echo 'ERROR: pyproject.toml not found. Run this script from the enterprise-data-strategy-agent repo root.'
  exit 1
fi
PYTHON_BIN="${PYTHON:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then PYTHON_BIN=python; fi
"$PYTHON_BIN" --version
if [ ! -d .venv ]; then "$PYTHON_BIN" -m venv .venv; fi
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
if [ -f requirements.txt ]; then python -m pip install -r requirements.txt; fi
enterprise-data-strategy-agent doctor
echo 'Setup complete. Run ./run_demo.sh to generate example outputs.'
