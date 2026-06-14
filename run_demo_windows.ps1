$ErrorActionPreference = 'Stop'
if (!(Test-Path 'pyproject.toml')) { Write-Error 'ERROR: pyproject.toml not found. Run this file from the enterprise-data-strategy-agent repo root. If PowerShell blocks this script, run: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass'; exit 1 }
if (Test-Path '.\.venv\Scripts\Activate.ps1') { . .\.venv\Scripts\Activate.ps1 }
enterprise-data-strategy-agent doctor
enterprise-data-strategy-agent lint --input data\sample_domo_inventory.json --output examples\generated_lint_report.md --config config\sample_strategy_policy.yml
enterprise-data-strategy-agent analyze --input data\sample_domo_inventory.json --output examples\generated_strategy_brief.md --config config\sample_strategy_policy.yml
enterprise-data-strategy-agent plan --input data\sample_domo_inventory.json --output examples\generated_remediation_plan.md --json-output examples\generated_remediation_backlog.json --config config\sample_strategy_policy.yml
Write-Host 'Demo complete. Outputs were written to examples\.'
