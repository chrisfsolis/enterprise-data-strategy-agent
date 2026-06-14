# Enterprise Data Strategy Agent

A free, open-source enterprise data strategy assistant that uses synthetic Domo-style metadata as its first reference implementation to help data managers assess governance, trust, freshness, ownership, reporting risk, and trusted data product opportunities.

> This is not affiliated with, endorsed by, or sponsored by Domo. Domo-style metadata is used because many enterprise data managers use Domo concepts such as datasets, cards, dashboards, Beast Mode calculations, certification, ownership, and business reporting.

## Quickstart

Run all commands from the folder that contains `pyproject.toml`. Do not run `pip install -e .` from `C:\Users\Me` unless the repo is actually located there. The CLI is cross-platform; the shell, batch, and PowerShell files are convenience wrappers only.

### macOS / Linux

```bash
git clone <repo-url>
cd enterprise-data-strategy-agent
chmod +x setup.sh run_demo.sh doctor.sh
./setup.sh
./run_demo.sh
```

### Windows Command Prompt

```cmd
cd /d C:\path\to\enterprise-data-strategy-agent
setup_windows.bat
run_demo_windows.bat
```

### Windows PowerShell

```powershell
cd C:\path\to\enterprise-data-strategy-agent
.\setup_windows.ps1
.\run_demo_windows.ps1
```

If PowerShell blocks scripts, run this in the same PowerShell window, then retry:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Universal manual setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
enterprise-data-strategy-agent doctor
enterprise-data-strategy-agent --help
pytest -q
```

For Windows manual activation:

```cmd
.venv\Scripts\activate
```

## What it does

The agent reviews enterprise analytics metadata and generates practical markdown and JSON artifacts. It looks for stale data, uncertified executive assets, owner gaps, duplicate metrics, inconsistent names, weak stewardship, high-value dashboards using uncertified datasets, and opportunities to formalize trusted data products.

## Run

```bash
enterprise-data-strategy-agent doctor
enterprise-data-strategy-agent lint --input data/sample_domo_inventory.json --output examples/generated_lint_report.md --config config/sample_strategy_policy.yml
enterprise-data-strategy-agent analyze --input data/sample_domo_inventory.json --output examples/generated_strategy_brief.md --config config/sample_strategy_policy.yml
enterprise-data-strategy-agent plan --input data/sample_domo_inventory.json --output examples/generated_remediation_plan.md --json-output examples/generated_remediation_backlog.json --config config/sample_strategy_policy.yml
```

## Optional web UI

The project includes a lightweight Streamlit app. The CLI never launches Streamlit; run the UI explicitly from the repository root:

```bash
streamlit run app.py
```

## Documentation

- [Universal quickstart](docs/quickstart.md)
- [Windows quickstart](docs/windows_quickstart.md)
- [macOS/Linux quickstart](docs/mac_linux_quickstart.md)
- [Architecture](docs/architecture.md)
- [Strategy policy](docs/strategy_policy.md)
- [Remediation planning](docs/remediation_planning.md)

## Who this is for

- Enterprise data managers and analytics leaders
- Data governance owners and BI platform administrators
- Domo administrators evaluating metadata quality patterns
- Data-driven business teams preparing governance conversations

## Architecture overview

The project has a connector abstraction, a synthetic Domo mock connector, typed metadata models, an analyzer, a scoring engine, a linting engine, planning/backlog generators, and a markdown report generator. Future connectors can support Snowflake, Tableau, Power BI, Looker, dbt, Collibra, Alation, Atlan, and other systems.
