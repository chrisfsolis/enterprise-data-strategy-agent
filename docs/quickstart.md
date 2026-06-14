# Universal Quickstart

Clone the repo or extract the ZIP, then open a terminal in the `enterprise-data-strategy-agent` folder. Confirm you are in the right place with `dir pyproject.toml` on Windows or `test -f pyproject.toml && echo OK` on macOS/Linux.

## macOS/Linux

```bash
chmod +x setup.sh run_demo.sh doctor.sh
./setup.sh
./run_demo.sh
```

## Windows Command Prompt

```cmd
cd /d C:\path\to\enterprise-data-strategy-agent
setup_windows.bat
run_demo_windows.bat
```

## Windows PowerShell

```powershell
cd C:\path\to\enterprise-data-strategy-agent
.\setup_windows.ps1
.\run_demo_windows.ps1
```

If scripts are blocked, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and retry.

## Doctor and CLI commands

```bash
enterprise-data-strategy-agent doctor
enterprise-data-strategy-agent lint --input data/sample_domo_inventory.json --output examples/generated_lint_report.md --config config/sample_strategy_policy.yml
enterprise-data-strategy-agent analyze --input data/sample_domo_inventory.json --output examples/generated_strategy_brief.md --config config/sample_strategy_policy.yml
enterprise-data-strategy-agent plan --input data/sample_domo_inventory.json --output examples/generated_remediation_plan.md --json-output examples/generated_remediation_backlog.json --config config/sample_strategy_policy.yml
```

## Streamlit UI

The web UI is optional and explicit:

```bash
streamlit run app.py
```

## Common errors

- `pyproject.toml not found`: change into the repo root folder.
- `enterprise-data-strategy-agent is not recognized`: activate `.venv` and run `pip install -e .`.
- `permission denied`: run `chmod +x setup.sh run_demo.sh doctor.sh`.
- `python not found`: try `python3` on macOS/Linux or install Python 3.11+.
