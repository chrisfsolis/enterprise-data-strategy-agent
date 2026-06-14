# Enterprise Data Strategy Agent

A free, open-source enterprise data strategy assistant that uses synthetic Domo-style metadata as its first reference implementation to help data managers assess governance, trust, freshness, ownership, reporting risk, and trusted data product opportunities.

> This is not affiliated with, endorsed by, or sponsored by Domo. It is not a Domo product, Domo replacement, or official Domo tool. Domo-style metadata is used because many enterprise data managers use Domo concepts such as datasets, cards, dashboards, Beast Mode calculations, certification, ownership, and business reporting.

## What it does

The agent reviews enterprise analytics metadata and generates a practical markdown strategy brief. It looks for stale data, uncertified executive assets, owner gaps, duplicate metrics, inconsistent names, weak stewardship, high-value dashboards using uncertified datasets, and opportunities to formalize trusted data products.

It also includes a dedicated metadata lint command so enterprise data managers can run a fast governance quality check before generating a full strategy report.

## Who this is for

- Enterprise data managers and analytics leaders
- Data governance owners and BI platform administrators
- Domo administrators evaluating metadata quality patterns
- Data-driven business teams preparing governance conversations

## What the agent analyzes

Datasets, dashboards/cards, owners, departments, refresh cadence, last refresh dates, certification status, row counts, sensitivity, usage, business criticality, Domo Beast Mode-style calculated metrics, and dataset-to-dashboard relationships.

## Example use cases

- Prepare a governance review for executive reporting.
- Identify stale or manually refreshed datasets feeding critical dashboards.
- Find duplicate revenue calculations before leadership reviews.
- Propose trusted data products for Finance, Sales, Customer Success, Operations, and Product.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements.txt
```


### Optional web UI

The project also includes a lightweight Streamlit app for users who prefer an upload-and-download workflow. Install the optional UI dependencies after activating your virtual environment:

```bash
pip install -e ".[ui]"
```

Run the app from the repository root:

```bash
streamlit run src/enterprise_data_strategy_agent/ui.py
```

In the browser, upload an inventory JSON file such as `data/sample_domo_inventory.json`. The UI validates the payload, runs the analyzer, displays health scores, top risks, quick wins, risky dashboards, stale datasets, trusted data product opportunities, and provides a markdown report preview with a download button.

## Run

Generate the full enterprise data strategy brief:

```bash
enterprise-data-strategy-agent analyze --input data/sample_domo_inventory.json --output examples/generated_strategy_brief.md
```

Run the standalone metadata lint check:

```bash
enterprise-data-strategy-agent lint --input data/sample_domo_inventory.json
```

Optionally write a markdown lint report:

```bash
enterprise-data-strategy-agent lint --input data/sample_domo_inventory.json --output examples/generated_lint_report.md
```

Example analyze output:

```text
Enterprise data strategy markdown output generated: examples/generated_strategy_brief.md
```

Example lint output:

```text
Inventory structural validation passed: data/sample_domo_inventory.json
Datasets: 8
Dashboards/cards: 8
Metadata lint summary:
- Total findings: ...
- Critical: ...
- High: ...
- Medium: ...
- Low: ...
```

## Validation vs. linting

Structural validation answers: “Is this inventory payload shaped correctly enough to parse?” It rejects malformed JSON, missing required top-level sections, invalid dates, and fields that cannot be converted into the typed inventory model.

Metadata linting answers: “Does this parsed inventory reveal business, quality, or governance issues?” Lint findings are advisory and do not block parsing. For example, dashboards/cards may reference dataset IDs that are not present in the inventory. That is valid structure, but the lint command reports it as a governance issue so a data manager can fix missing lineage or stale references.

Lint findings include severity levels (`critical`, `high`, `medium`, and `low`), a rule ID, affected object details, and a practical recommendation. Rules cover missing upstream datasets, missing owners, executive dashboards using uncertified datasets, sensitive data without stewardship, stale data, manually refreshed critical reporting paths, duplicate metrics, high-row-count/low-usage datasets, certified dashboards with uncertified dependencies, orphan dashboards, and unused datasets.

## Why linting matters for enterprise data managers

Metadata linting gives data managers a pre-flight governance checklist before a full strategy report or executive review. It helps prioritize fixes that improve trust in leadership reporting, clarify ownership, reduce risk around sensitive data, and identify cleanup opportunities without modifying the source BI or data platform. This version uses synthetic Domo-style metadata as a reference implementation and is not an official Domo product.

## Example report snippet

```markdown
## Health Scores
- Overall enterprise data strategy health: **.../100**
- Governance score: **.../100**
```

## Architecture overview

The project has a connector abstraction, a synthetic Domo mock connector, typed metadata models, an analyzer, a scoring engine, and a markdown report generator. Future connectors can support Snowflake, Tableau, Power BI, Looker, dbt, Collibra, Alation, Atlan, and other systems.

## Roadmap

1. Synthetic Domo-style metadata analyzer
2. Domo read-only connector
3. Streamlit or lightweight web UI
4. Governance workflow recommendations
5. AI-assisted natural language strategy assistant
6. Additional platform connectors
7. Optional embedded or app-based experiences

## Sample data

All sample data is synthetic and intentionally includes governance and reporting issues for demonstration purposes.

## License

MIT License. See [LICENSE](LICENSE).

## Strategy Policy Configuration

Strategy policy configuration matters because governance expectations are not universal. A startup, regulated enterprise, finance team, and operations team may all disagree on what counts as stale data, when certification is mandatory, who must own sensitive data, and how much executive-reporting risk is acceptable. The optional policy file moves those assumptions out of code and into a YAML file that an enterprise data manager can review and tune.

Run analysis with a policy file:

```bash
enterprise-data-strategy-agent analyze \
  --input data/sample_domo_inventory.json \
  --output examples/generated_strategy_brief.md \
  --config config/sample_strategy_policy.yml
```

Run metadata linting with the same policy file:

```bash
enterprise-data-strategy-agent lint \
  --input data/sample_domo_inventory.json \
  --output examples/generated_lint_report.md \
  --config config/sample_strategy_policy.yml
```

Example policy snippet:

```yaml
organization:
  name: Acme Enterprise
  industry: SaaS and Digital Operations
  data_maturity_stage: Governed self-service analytics
  primary_platform: Domo
  strategy_owner_role: Enterprise Data Manager

freshness_thresholds:
  daily_dataset_stale_after_days: 2
  weekly_dataset_stale_after_days: 10
  monthly_dataset_stale_after_days: 35
  manual_dataset_review_after_days: 14

severity_overrides:
  stale_dataset: high
  executive_dashboard_uncertified_source: critical
```

Different organizations may have different freshness, certification, ownership, sensitivity, and reporting-risk expectations. Use `config/sample_strategy_policy.yml` as a starting point and adjust thresholds, scoring weights, severity overrides, trusted data product domains, and stakeholder roles to match your operating model.

## Remediation planning

The `plan` command turns lint findings, strategy risks, and score gaps into an executable remediation backlog for enterprise data managers:

```bash
enterprise-data-strategy-agent plan \
  --input data/sample_domo_inventory.json \
  --output examples/generated_remediation_plan.md
```

Use the same policy file as analysis and linting:

```bash
enterprise-data-strategy-agent plan \
  --input data/sample_domo_inventory.json \
  --output examples/generated_remediation_plan.md \
  --config config/sample_strategy_policy.yml
```

Generate both markdown and machine-readable JSON:

```bash
enterprise-data-strategy-agent plan \
  --input data/sample_domo_inventory.json \
  --output examples/generated_remediation_plan.md \
  --json-output examples/generated_remediation_backlog.json \
  --config config/sample_strategy_policy.yml
```

### How lint, analyze, and plan work together

1. `lint` performs a focused metadata-quality and governance check with rule IDs, severities, and recommendations.
2. `analyze` combines lint findings with strategic scoring, top risks, trusted data product opportunities, and a strategy brief.
3. `plan` converts those findings into prioritized remediation items with owners, stakeholders, effort, impact, time horizon, recommended actions, and success measures.

Example remediation item:

```markdown
- REM-001: Review and remediate stale dataset
  - Priority: P0 or P1 depending on severity, executive reporting use, and business criticality
  - Owner: Enterprise Data Manager
  - Supporting stakeholders: Domo Admin, domain business owner, executive sponsor when relevant
  - Recommended action: Confirm whether the dataset is still required, refresh it, define an SLA, or retire dependent reporting.
  - Success measure: Stale executive or high-criticality datasets remediated or formally retired.
```

Remediation planning matters because enterprise data managers need more than a list of problems. They need a sequenced backlog they can review with Finance, Sales, Operations, Compliance, BI admins, and executive sponsors. The plan makes governance work discussable, assignable, and measurable.

The tool is advisory and read-only. It does not make changes to Domo or any other platform.

## Run the Web UI

The project includes a lightweight Streamlit interface for demoing the metadata governance, strategy brief, and remediation planning workflows to enterprise data managers, analytics leaders, Domo admins, and non-technical stakeholders.

### Install

```bash
python -m pip install -r requirements.txt
```

For editable development installs, you can also run:

```bash
python -m pip install -e .
```

### Launch

```bash
streamlit run app.py
```

### What the UI supports

- Use the bundled synthetic sample inventory from `data/sample_domo_inventory.json`.
- Upload a custom Domo-style JSON metadata inventory.
- Use the default policy, bundled sample policy from `config/sample_strategy_policy.yml`, or an uploaded YAML policy.
- Run metadata linting, enterprise data strategy analysis/scoring, and remediation planning from the browser.
- Preview the generated metadata lint report, enterprise data strategy brief, remediation plan, and remediation backlog.
- Download the strategy brief markdown, lint report markdown, remediation plan markdown, and backlog JSON.

### Screenshot

_Screenshot placeholder: add a screenshot of the Streamlit Overview tab after launching `streamlit run app.py`._

The included sample data is synthetic and Domo-style only. This repository is independent and unofficial, does not require real Domo credentials, and does not modify Domo or any other source platform.
