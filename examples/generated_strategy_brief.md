# Enterprise Data Strategy Brief

## Executive Summary
The analytics environment shows an overall health score of 49/100. The strongest immediate opportunities are to improve ownership, certify executive reporting paths, remediate stale datasets, and standardize duplicate metric logic before it reaches business-critical dashboards.

## Platform Context
This version analyzes synthetic metadata from the Domo-style reference metadata for datasets, cards, dashboards, owners, certification, calculated metrics, sensitivity, usage, and refresh patterns. This project is independent and is not affiliated with, endorsed by, or sponsored by Domo. Domo-style metadata is used only as the first reference implementation.

## Strategy Policy Context
- Organization name: Acme Enterprise
- Industry: SaaS and Digital Operations
- Data maturity stage: Governed self-service analytics
- Primary platform: Domo
- Strategy owner role: Enterprise Data Manager
- Policy source: config/sample_strategy_policy.yml
- Major assumptions: daily datasets stale after 2 days; weekly after 10 days; monthly after 35 days; manual datasets reviewed after 14 days; high-row-count datasets start at 750,000 rows; executive certification required is True.

## Health Scores
- Overall enterprise data strategy health: **49/100**
  - Why: Governance contributes 30% of the overall score. Trust contributes 25% of the overall score. Freshness contributes 20% of the overall score. Ownership contributes 15% of the overall score. Executive reporting risk contributes 10% of the overall score.
  - Governance: bonus +15.3 points — Governance contributes 30% of the overall score.
  - Trust: bonus +13.0 points — Trust contributes 25% of the overall score.
  - Freshness: bonus +9.8 points — Freshness contributes 20% of the overall score.
  - Ownership: bonus +9.3 points — Ownership contributes 15% of the overall score.
  - Executive reporting risk: bonus +2.0 points — Executive reporting risk contributes 10% of the overall score.
- Governance score: **51/100**
  - Why: 5 assets that require certification are not certified. 4 high-sensitivity datasets lack a named steward. 2 datasets use manual refreshes, which weakens repeatable governance.
  - Uncertified expected assets: penalty -8.8 points — 5 assets that require certification are not certified.
  - Sensitive datasets without stewards: penalty -32.0 points — 4 high-sensitivity datasets lack a named steward.
  - Manual refresh cadence: penalty -8.0 points — 2 datasets use manual refreshes, which weakens repeatable governance.
- Trust score: **52/100**
  - Why: Governance contributes 45% of trust. Freshness contributes 35% of trust. Ownership contributes 20% of trust.
  - Governance contribution: bonus +22.9 points — Governance contributes 45% of trust.
  - Freshness contribution: bonus +17.1 points — Freshness contributes 35% of trust.
  - Ownership contribution: bonus +12.4 points — Ownership contributes 20% of trust.
- Freshness score: **49/100**
  - Why: 6 of 10 datasets exceed configured stale-data windows. 2 datasets rely on manual refreshes rather than automated freshness controls.
  - Stale datasets: penalty -45.0 points — 6 of 10 datasets exceed configured stale-data windows.
  - Manual refresh cadence: penalty -6.0 points — 2 datasets rely on manual refreshes rather than automated freshness controls.
- Ownership score: **62/100**
  - Why: 4 assets are missing business owners. 4 sensitive datasets have no steward assigned.
  - Missing owners: penalty -14.0 points — 4 assets are missing business owners.
  - Sensitive stewardship gaps: penalty -24.0 points — 4 sensitive datasets have no steward assigned.
- Executive reporting risk score: **20/100**
  - Why: 4 of 4 executive or critical dashboards have certification, owner, or upstream data risks.
  - Risky executive dashboards: penalty -80.0 points — 4 of 4 executive or critical dashboards have certification, owner, or upstream data risks.

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
Strategic trust findings below are generated separately from the metadata-quality lint results that follow.
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

## Metadata Lint Summary
- Total lint findings: **22**
- Critical: **6**
- High: **12**
- Medium: **2**
- Low: **2**
- Highest-priority examples:
  - **CRITICAL LINT004** dashboard `card_board_pack`: Executive dashboard uses uncertified datasets. Recommendation: Certify upstream datasets or clearly label the dashboard as not certified for executive decision-making.
  - **CRITICAL LINT004** dashboard `card_exec_scorecard`: Executive dashboard uses uncertified datasets. Recommendation: Certify upstream datasets or clearly label the dashboard as not certified for executive decision-making.
  - **CRITICAL LINT005** dataset `ds_cs_health`: Sensitive dataset lacks stewardship. Recommendation: Assign a data steward responsible for access, definitions, and quality expectations.
  - **CRITICAL LINT005** dataset `ds_exec_kpi`: Sensitive dataset lacks stewardship. Recommendation: Assign both an owner and a steward before broadening access or certification.
  - **CRITICAL LINT005** dataset `ds_hr_headcount`: Sensitive dataset lacks stewardship. Recommendation: Assign both an owner and a steward before broadening access or certification.

## Metadata Quality Lint Findings
- **CRITICAL LINT004** dashboard `card_board_pack`: Executive dashboard is powered by uncertified datasets: Executive KPI Snapshot. Recommended action: Certify upstream datasets or clearly label the dashboard as not certified for executive decision-making.
- **CRITICAL LINT004** dashboard `card_exec_scorecard`: Executive dashboard is powered by uncertified datasets: Executive KPI Snapshot, Sales Bookings Pipeline. Recommended action: Certify upstream datasets or clearly label the dashboard as not certified for executive decision-making.
- **CRITICAL LINT005** dataset `ds_cs_health`: Sensitive dataset has no named steward. Recommended action: Assign a data steward responsible for access, definitions, and quality expectations.
- **CRITICAL LINT005** dataset `ds_exec_kpi`: Sensitive dataset has no steward or owner. Recommended action: Assign both an owner and a steward before broadening access or certification.
- **CRITICAL LINT005** dataset `ds_hr_headcount`: Sensitive dataset has no steward or owner. Recommended action: Assign both an owner and a steward before broadening access or certification.
- **CRITICAL LINT005** dataset `ds_product_usage`: Sensitive dataset has no named steward. Recommended action: Assign a data steward responsible for access, definitions, and quality expectations.
- **HIGH LINT002** dataset `ds_exec_kpi`: Dataset has no accountable business owner. Recommended action: Assign a business owner responsible for definitions, quality expectations, and escalation.
- **HIGH LINT002** dataset `ds_hr_headcount`: Dataset has no accountable business owner. Recommended action: Assign a business owner responsible for definitions, quality expectations, and escalation.
- **HIGH LINT006** dataset `ds_budget_plan`: Dataset last refreshed on 2026-01-31 is stale for its manual cadence. Recommended action: Refresh the dataset, correct the cadence metadata, or document why stale data is acceptable.
- **HIGH LINT006** dataset `ds_cs_health`: Dataset last refreshed on 2026-05-20 is stale for its weekly cadence. Recommended action: Refresh the dataset, correct the cadence metadata, or document why stale data is acceptable.
- **HIGH LINT006** dataset `ds_exec_kpi`: Dataset last refreshed on 2026-04-15 is stale for its manual cadence. Recommended action: Refresh the dataset, correct the cadence metadata, or document why stale data is acceptable.
- **HIGH LINT006** dataset `ds_hr_headcount`: Dataset last refreshed on 2026-03-31 is stale for its monthly cadence. Recommended action: Refresh the dataset, correct the cadence metadata, or document why stale data is acceptable.
- **HIGH LINT006** dataset `ds_product_usage`: Dataset last refreshed on 2026-05-01 is stale for its daily cadence. Recommended action: Refresh the dataset, correct the cadence metadata, or document why stale data is acceptable.
- **HIGH LINT006** dataset `ds_sales_bookings`: Dataset last refreshed on 2026-06-10 is stale for its daily cadence. Recommended action: Refresh the dataset, correct the cadence metadata, or document why stale data is acceptable.
- **HIGH LINT007** dashboard `card_board_pack`: High-criticality dashboard uses manually refreshed datasets: Executive KPI Snapshot, Annual Budget Plan. Recommended action: Move these datasets to scheduled refreshes with freshness alerts and documented SLAs.
- **HIGH LINT007** dashboard `card_exec_scorecard`: High-criticality dashboard uses manually refreshed datasets: Executive KPI Snapshot. Recommended action: Move these datasets to scheduled refreshes with freshness alerts and documented SLAs.
- **HIGH LINT007** dashboard `dash_fin_close`: High-criticality dashboard uses manually refreshed datasets: Annual Budget Plan. Recommended action: Move these datasets to scheduled refreshes with freshness alerts and documented SLAs.
- **HIGH LINT010** dashboard `card_marketing_roi`: Certified dashboard is backed by uncertified datasets: Sales Bookings Pipeline. Recommended action: Certify upstream datasets or remove dashboard certification until dependencies are trusted.
- **MEDIUM LINT003** dashboard `card_exec_scorecard`: Dashboard/card has no accountable business owner. Recommended action: Assign a business owner who can approve definitions, certification, and remediation decisions.
- **MEDIUM LINT003** dashboard `dash_people_plan`: Dashboard/card has no accountable business owner. Recommended action: Assign a business owner who can approve definitions, certification, and remediation decisions.
- **LOW LINT009** dataset `ds_ops_fulfillment`: Dataset has 9,400,000 rows but low usage. Recommended action: Review whether this dataset should be archived, summarized, promoted, or redesigned as a governed data product.
- **LOW LINT009** dataset `ds_product_usage`: Dataset has 18,800,000 rows but low usage. Recommended action: Review whether this dataset should be archived, summarized, promoted, or redesigned as a governed data product.

## Dashboard and Reporting Risk
- Executive Scorecard: uncertified, missing owner, uses uncertified datasets, powered by stale data
- Board Revenue Pack: uncertified, uses uncertified datasets, powered by stale data
- Finance Close Dashboard: powered by stale data
- Sales Forecast Command Center: uncertified, uses uncertified datasets, powered by stale data

## Trusted Data Product Opportunities
- Executive Reporting Trusted Data Product
- Finance Trusted Data Product
- Sales Trusted Data Product
- Customer Success Trusted Data Product
- Operations Trusted Data Product

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
- Meet with Enterprise Data Manager to align policy thresholds, ownership, certification, and escalation expectations.
- Meet with Domo Admin to align policy thresholds, ownership, certification, and escalation expectations.
- Meet with Finance Leader to align policy thresholds, ownership, certification, and escalation expectations.
- Meet with Sales Operations Leader to align policy thresholds, ownership, certification, and escalation expectations.
- Meet with Customer Success Operations Leader to align policy thresholds, ownership, certification, and escalation expectations.
- Meet with Data Governance Owner to align policy thresholds, ownership, certification, and escalation expectations.
- Meet with Security or Compliance Partner to align policy thresholds, ownership, certification, and escalation expectations.
