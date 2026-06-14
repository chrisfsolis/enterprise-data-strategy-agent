#!/usr/bin/env sh
set -eu
if [ ! -f pyproject.toml ]; then
  echo 'ERROR: pyproject.toml not found. Run this script from the enterprise-data-strategy-agent repo root.'
  exit 1
fi
if [ -f .venv/bin/activate ]; then . .venv/bin/activate; fi
enterprise-data-strategy-agent doctor
enterprise-data-strategy-agent lint --input data/sample_domo_inventory.json --output examples/generated_lint_report.md --config config/sample_strategy_policy.yml
enterprise-data-strategy-agent analyze --input data/sample_domo_inventory.json --output examples/generated_strategy_brief.md --config config/sample_strategy_policy.yml
enterprise-data-strategy-agent plan --input data/sample_domo_inventory.json --output examples/generated_remediation_plan.md --json-output examples/generated_remediation_backlog.json --config config/sample_strategy_policy.yml
echo 'Demo complete. Outputs were written to examples/.'
