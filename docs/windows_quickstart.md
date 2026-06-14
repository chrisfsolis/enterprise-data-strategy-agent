# Windows Quickstart

Find the repo folder in File Explorer, click the address bar, type `cmd`, and press Enter. Confirm `pyproject.toml` exists with `dir pyproject.toml`.

## Command Prompt

```cmd
setup_windows.bat
run_demo_windows.bat
```

Manual activation:

```cmd
.venv\Scripts\activate
```

## PowerShell

```powershell
.\setup_windows.ps1
.\run_demo_windows.ps1
```

If blocked, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Fixes

- `pyproject.toml not found`: use `cd /d C:\path\to\enterprise-data-strategy-agent`.
- `enterprise-data-strategy-agent is not recognized`: activate `.venv`, then run `python -m pip install -e .`.
- To run the UI: `streamlit run app.py`.
