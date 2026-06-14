#!/usr/bin/env sh
set -eu
if [ ! -f pyproject.toml ]; then
  echo 'ERROR: pyproject.toml not found. Run this script from the enterprise-data-strategy-agent repo root.'
  exit 1
fi
if [ -f .venv/bin/activate ]; then . .venv/bin/activate; fi
if python -c "import enterprise_data_strategy_agent.doctor" >/dev/null 2>&1; then
  python -m enterprise_data_strategy_agent.doctor
else
  echo 'The package is not installed yet. Run ./setup.sh first.'
  exit 1
fi
