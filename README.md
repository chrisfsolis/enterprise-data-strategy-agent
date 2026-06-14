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
