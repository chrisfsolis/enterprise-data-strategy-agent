$ErrorActionPreference = 'Stop'
Write-Host "Current directory: $(Get-Location)"
if (!(Test-Path 'pyproject.toml')) { Write-Error 'ERROR: pyproject.toml not found. Run this file from the enterprise-data-strategy-agent repo root. If PowerShell blocks this script, run: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass'; exit 1 }
python --version
if (!(Test-Path '.venv')) { python -m venv .venv }
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
if (Test-Path 'requirements.txt') { python -m pip install -r requirements.txt }
enterprise-data-strategy-agent doctor
Write-Host 'Setup complete. Run .\run_demo_windows.ps1 to generate example outputs.'
