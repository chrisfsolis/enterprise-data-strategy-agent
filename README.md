# Enterprise Data Strategy Agent

A free, open-source enterprise data strategy assistant that uses synthetic Domo-style metadata as its first reference implementation to help data managers assess governance, trust, freshness, ownership, reporting risk, and trusted data product opportunities.

> This is not affiliated with, endorsed by, or sponsored by Domo. It is not a Domo product, Domo replacement, or official Domo tool. Domo-style metadata is used because many enterprise data managers use Domo concepts such as datasets, cards, dashboards, Beast Mode calculations, certification, ownership, and business reporting.

## What it does

The agent reviews enterprise analytics metadata and generates a practical markdown strategy brief. It looks for stale data, uncertified executive assets, owner gaps, duplicate metrics, inconsistent names, weak stewardship, high-value dashboards using uncertified datasets, and opportunities to formalize trusted data products.

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

## Run

```bash
enterprise-data-strategy-agent analyze --input data/sample_domo_inventory.json --output examples/generated_strategy_brief.md
```

Example output:

```text
Enterprise data strategy brief generated: examples/generated_strategy_brief.md
```

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
