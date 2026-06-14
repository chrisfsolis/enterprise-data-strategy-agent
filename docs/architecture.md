# Architecture

## Data input layer
The starter project reads a local JSON inventory with synthetic Domo-style metadata. This keeps demos credential-free while preserving realistic enterprise metadata fields.

## Connector abstraction
`MetadataConnector` defines a read-only loading contract so future platforms can provide their own metadata inventories without changing the analyzer.

## Domo mock connector
`DomoMockConnector` loads and validates the sample inventory. It does not call Domo APIs and does not require credentials.

## Analysis engine
The analyzer reviews freshness, certification, ownership, sensitivity, stewardship, usage, criticality, dashboard dependencies, and duplicate metric candidates.

## Scoring engine
The scoring engine returns health scores from 0 to 100 for overall strategy health, governance, trust, freshness, ownership, and executive reporting risk.

## Report generator
The report generator produces a consultant-style markdown strategy brief for enterprise data managers.

## Future real Domo API connector
A future connector should use read-only credentials, least privilege scopes, explicit tenant configuration, rate-limit handling, and safe local export controls.

## Future UI layer
A lightweight Streamlit or web UI could let users upload inventory files, review findings interactively, and export briefs.

## Future AI assistant layer
An AI layer could help users ask natural-language questions about risks, definitions, and remediation plans while grounding answers in metadata findings.

## Configurable Strategy Policy Layer

The policy layer sits between raw metadata ingestion and advisory outputs. `src/enterprise_data_strategy_agent/policy.py` defines typed defaults and loads optional YAML policy files. The CLI passes the loaded policy into analysis, scoring, linting, and markdown report generation so the same metadata can be evaluated against organization-specific expectations.

Policy-aware components include:

- **Analyzer**: uses policy-aware freshness checks, lint findings, trusted data product domains, and stakeholder roles.
- **Scoring engine**: uses configured freshness thresholds and adjustable overall scoring weights.
- **Linting engine**: uses configured stale-data windows, high-row-count thresholds, and severity overrides.
- **Reports**: include policy context so readers know whether default or organization-specific assumptions were applied.

If no `--config` argument is provided, the agent uses built-in defaults to preserve backward-compatible behavior for demos and existing automation.

## Remediation planning layer

The remediation planning layer sits after validation, linting, analysis, and scoring. `planning.py` consumes the parsed inventory, policy-aware analysis result, lint findings, and score explanations, then produces a prioritized remediation backlog. `backlog.py` defines the `RemediationItem` model and summary helpers used by markdown and JSON outputs.

The `plan` CLI command runs the full read-only flow:

1. Load and structurally validate inventory metadata.
2. Load default policy settings or an optional policy file.
3. Run metadata linting.
4. Run strategy analysis and scoring.
5. Convert findings into a prioritized remediation backlog.
6. Generate a markdown execution plan and optional JSON backlog.

This keeps remediation advisory and explainable. The agent recommends work, owners, stakeholders, success measures, and timing, but it does not automatically edit source BI assets, datasets, permissions, or workflows.

## Web UI Layer

The Streamlit UI is a thin orchestration layer on top of the CLI-first strategy engine. It is intentionally kept lightweight so the reusable business logic remains in importable modules rather than in browser-rendering code.

- `app.py` is the root Streamlit entry point and imports the packaged UI runner.
- `src/enterprise_data_strategy_agent/ui/streamlit_app.py` renders the browser experience, sidebar selectors, tabs, previews, and download buttons.
- `src/enterprise_data_strategy_agent/ui/__init__.py` provides small, testable UI helper functions that load samples, parse uploads, summarize metadata, format table rows, and generate report artifacts.

The UI sits above the existing architecture:

1. **Inventory loading** — bundled sample metadata is loaded through the existing sample loader and connector path; uploaded JSON is parsed and validated through the inventory model validation helpers.
2. **Policy loading** — the default policy, bundled sample policy, or uploaded YAML policy are loaded through the existing strategy policy loader.
3. **Linting** — metadata findings are produced by `lint_inventory` and rendered as metrics, filterable tables, and markdown report previews.
4. **Analysis/scoring** — health scores, top risks, and the strategy brief are produced by the existing analyzer and report generator.
5. **Remediation planning** — the remediation backlog, summary dimensions, markdown plan, and JSON backlog come from the existing planning and backlog modules.
6. **Report generation** — the UI exposes generated markdown and JSON artifacts as browser previews and download buttons without changing the report-generation logic.

The UI does not require credentials, does not call real Domo APIs, and does not modify Domo, Snowflake, BI tools, catalogs, or any other source platform. Domo-style metadata remains the first reference implementation for the current release.
