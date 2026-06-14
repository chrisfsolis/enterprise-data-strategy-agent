@echo off
echo Current directory: %CD%
if not exist pyproject.toml (
  echo ERROR: pyproject.toml not found. Run this file from the enterprise-data-strategy-agent repo root.
  pause
  exit /b 1
)
python --version || exit /b 1
if not exist .venv python -m venv .venv || exit /b 1
call .venv\Scripts\activate.bat || exit /b 1
python -m pip install --upgrade pip || exit /b 1
python -m pip install -e . || exit /b 1
if exist requirements.txt python -m pip install -r requirements.txt || exit /b 1
enterprise-data-strategy-agent doctor || exit /b 1
echo Setup complete. Run run_demo_windows.bat to generate example outputs.
pause
