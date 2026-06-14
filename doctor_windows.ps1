$ErrorActionPreference = 'Stop'
if (!(Test-Path 'pyproject.toml')) { Write-Error 'ERROR: pyproject.toml not found. Run this file from the enterprise-data-strategy-agent repo root. If PowerShell blocks this script, run: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass'; exit 1 }
if (Test-Path '.\.venv\Scripts\Activate.ps1') { . .\.venv\Scripts\Activate.ps1 }
try { python -c "import enterprise_data_strategy_agent.doctor" } catch { Write-Error 'The package is not installed yet. Run .\setup_windows.ps1 first.'; exit 1 }
python -m enterprise_data_strategy_agent.doctor
