@echo off
if not exist pyproject.toml (
  echo ERROR: pyproject.toml not found. Run this file from the enterprise-data-strategy-agent repo root.
  pause
  exit /b 1
)
if exist .venv\Scripts\activate.bat call .venv\Scripts\activate.bat
python -c "import enterprise_data_strategy_agent.doctor" >nul 2>nul
if errorlevel 1 (
  echo The package is not installed yet. Run setup_windows.bat first.
  pause
  exit /b 1
)
python -m enterprise_data_strategy_agent.doctor
pause
