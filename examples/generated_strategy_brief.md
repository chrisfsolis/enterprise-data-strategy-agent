# Enterprise Data Strategy Brief

## Executive Summary
The analytics environment shows an overall health score of 44/100. The strongest immediate opportunities are to improve ownership, certify executive reporting paths, remediate stale datasets, and standardize duplicate metric logic before it reaches business-critical dashboards.

## Platform Context
This version analyzes synthetic metadata from the Domo-style reference metadata for datasets, cards, dashboards, owners, certification, calculated metrics, sensitivity, usage, and refresh patterns. This project is independent and is not affiliated with, endorsed by, or sponsored by Domo. Domo-style metadata is used only as the first reference implementation.

## Health Scores
- Overall enterprise data strategy health: **44/100**
- Governance score: **41/100**
- Trust score: **48/100**
- Freshness score: **49/100**
- Ownership score: **62/100**
- Executive reporting risk score: **20/100**

## Top Findings
- 6 datasets are stale, including Sales Bookings Pipeline, Customer Success Health Scores, Product Usage Telemetry.
- 4 executive or critical dashboards have reporting risk.
- 4 assets are missing clear business owners.
- Revenue-related metrics appear duplicated or inconsistently named across datasets.
- Sensitive datasets lack named stewardship: Customer Success Health Scores, Product Usage Telemetry, Executive KPI Snapshot, Workforce Headcount Planning.

## Governance Gaps
- Require owners and stewards for certified and sensitive datasets.
- Separate experimental dashboards from certified executive reporting surfaces.
- Standardize calculated metric naming, definitions, and approval workflow.
- Review high-row-count, low-usage datasets for archiving or data product redesign.

## Data Quality and Trust Issues
- Stale dataset: Sales Bookings Pipeline
- Stale dataset: Customer Success Health Scores
- Stale dataset: Product Usage Telemetry
- Stale dataset: Executive KPI Snapshot
- Stale dataset: Workforce Headcount Planning
- Stale dataset: Annual Budget Plan
- Duplicate metric candidate: Net Revenue and Revenue
- Duplicate metric candidate: Net Revenue and Total Revenue
- Duplicate metric candidate: Revenue and Total Revenue
- Manual refreshes and inconsistent calculation names should be treated as trust risks, not only operational cleanup.

## Dashboard and Reporting Risk
- Executive Scorecard: uncertified, missing owner, uses uncertified datasets, powered by stale data
- Board Revenue Pack: uncertified, uses uncertified datasets, powered by stale data
- Finance Close Dashboard: powered by stale data
- Sales Forecast Command Center: uncertified, uses uncertified datasets, powered by stale data

## Trusted Data Product Opportunities
- Executive KPI Certified Data Product
- Finance Revenue and Bookings Data Product
- Sales Pipeline and Forecast Data Product
- Customer Health and Renewal Data Product
- Operations Fulfillment and SLA Data Product

## Recommended 30/60/90 Day Plan
### 30 days
- Confirm owners, stewards, and business criticality for every executive reporting asset.
- Triage stale and manually refreshed datasets that feed critical dashboards.
- Document standard definitions for revenue, churn, pipeline, and active customer metrics.
### 60 days
- Create certified domain datasets for Finance, Sales, Customer Success, and Executive Reporting.
- Rationalize duplicate cards and dashboards with overlapping KPI logic.
- Introduce metadata review ceremonies for ownership, sensitivity, and certification changes.
### 90 days
- Launch trusted data product scorecards with owners, SLAs, definitions, and known limitations.
- Automate freshness and certification exception reporting.
- Prepare a read-only connector roadmap for live platform metadata ingestion.

## Domo-Oriented Recommendations
Use certified datasets for executive paths, assign card and dashboard owners, standardize Beast Mode-style calculations, rationalize overlapping dashboards, configure alerts for freshness exceptions, route certification through governance workflows, and review metadata on a recurring cadence.

## Future Platform Opportunities
The same pattern can expand to Snowflake, Tableau, Power BI, Looker, dbt, Collibra, Alation, Atlan, and other analytics or governance systems by implementing additional read-only metadata connectors.

## Next Steps
- Assign owners to high-usage dashboards and critical datasets with missing accountability.
- Certify executive dashboards only after upstream datasets meet freshness and ownership expectations.
- Create a shared revenue metric definition and retire duplicate Beast Mode-style calculations.
- Move manually refreshed critical datasets onto documented schedules or alerts.

## Suggested Stakeholder Conversations
- Meet Finance and Sales leaders to align on revenue metric definitions.
- Meet executive reporting owners to agree on certification standards and escalation paths.
- Meet BI administrators to design recurring metadata quality reviews.
- Meet security and governance owners to clarify stewardship for sensitive data.
