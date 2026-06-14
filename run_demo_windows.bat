@echo off
if not exist pyproject.toml (
  echo ERROR: pyproject.toml not found. Run this file from the enterprise-data-strategy-agent repo root.
  pause
  exit /b 1
)
if exist .venv\Scripts\activate.bat call .venv\Scripts\activate.bat
enterprise-data-strategy-agent doctor || exit /b 1
enterprise-data-strategy-agent lint --input data\sample_domo_inventory.json --output examples\generated_lint_report.md --config config\sample_strategy_policy.yml || exit /b 1
enterprise-data-strategy-agent analyze --input data\sample_domo_inventory.json --output examples\generated_strategy_brief.md --config config\sample_strategy_policy.yml || exit /b 1
enterprise-data-strategy-agent plan --input data\sample_domo_inventory.json --output examples\generated_remediation_plan.md --json-output examples\generated_remediation_backlog.json --config config\sample_strategy_policy.yml || exit /b 1
echo Demo complete. Outputs were written to examples\.
pause
