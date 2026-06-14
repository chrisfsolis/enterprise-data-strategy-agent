# Enterprise Data Metadata Lint Report

## Summary
Inventory generated at: 2026-06-14
Datasets: 10
Dashboards/cards: 10
Total findings: 22
- Critical: 2
- High: 12
- Medium: 6
- Low: 2

## Critical Findings
- **LINT005: Sensitive dataset lacks stewardship**
  - Affected: dataset `ds_exec_kpi` (Executive KPI Snapshot)
  - Detail: Sensitive dataset has no steward or owner.
  - Recommendation: Assign both an owner and a steward before broadening access or certification.
- **LINT005: Sensitive dataset lacks stewardship**
  - Affected: dataset `ds_hr_headcount` (Workforce Headcount Planning)
  - Detail: Sensitive dataset has no steward or owner.
  - Recommendation: Assign both an owner and a steward before broadening access or certification.

## High Findings
- **LINT002: Dataset owner is missing**
  - Affected: dataset `ds_exec_kpi` (Executive KPI Snapshot)
  - Detail: Dataset has no accountable business owner.
  - Recommendation: Assign a business owner responsible for definitions, quality expectations, and escalation.
- **LINT003: Dashboard or card owner is missing**
  - Affected: dashboard `card_exec_scorecard` (Executive Scorecard)
  - Detail: Dashboard/card has no accountable business owner.
  - Recommendation: Assign a business owner who can approve definitions, certification, and remediation decisions.
- **LINT004: Executive dashboard uses uncertified datasets**
  - Affected: dashboard `card_board_pack` (Board Revenue Pack)
  - Detail: Executive dashboard is powered by uncertified datasets: Executive KPI Snapshot.
  - Recommendation: Certify upstream datasets or clearly label the dashboard as not certified for executive decision-making.
- **LINT004: Executive dashboard uses uncertified datasets**
  - Affected: dashboard `card_exec_scorecard` (Executive Scorecard)
  - Detail: Executive dashboard is powered by uncertified datasets: Executive KPI Snapshot, Sales Bookings Pipeline.
  - Recommendation: Certify upstream datasets or clearly label the dashboard as not certified for executive decision-making.
- **LINT005: Sensitive dataset lacks stewardship**
  - Affected: dataset `ds_cs_health` (Customer Success Health Scores)
  - Detail: Sensitive dataset has no named steward.
  - Recommendation: Assign a data steward responsible for access, definitions, and quality expectations.
- **LINT005: Sensitive dataset lacks stewardship**
  - Affected: dataset `ds_product_usage` (Product Usage Telemetry)
  - Detail: Sensitive dataset has no named steward.
  - Recommendation: Assign a data steward responsible for access, definitions, and quality expectations.
- **LINT006: Dataset is stale**
  - Affected: dataset `ds_exec_kpi` (Executive KPI Snapshot)
  - Detail: Dataset last refreshed on 2026-04-15 is stale for its manual cadence.
  - Recommendation: Refresh the dataset, correct the cadence metadata, or document why stale data is acceptable.
- **LINT006: Dataset is stale**
  - Affected: dataset `ds_sales_bookings` (Sales Bookings Pipeline)
  - Detail: Dataset last refreshed on 2026-06-10 is stale for its daily cadence.
  - Recommendation: Refresh the dataset, correct the cadence metadata, or document why stale data is acceptable.
- **LINT007: Critical dashboard depends on manually refreshed data**
  - Affected: dashboard `card_board_pack` (Board Revenue Pack)
  - Detail: High-criticality dashboard uses manually refreshed datasets: Executive KPI Snapshot, Annual Budget Plan.
  - Recommendation: Move these datasets to scheduled refreshes with freshness alerts and documented SLAs.
- **LINT007: Critical dashboard depends on manually refreshed data**
  - Affected: dashboard `card_exec_scorecard` (Executive Scorecard)
  - Detail: High-criticality dashboard uses manually refreshed datasets: Executive KPI Snapshot.
  - Recommendation: Move these datasets to scheduled refreshes with freshness alerts and documented SLAs.
- **LINT007: Critical dashboard depends on manually refreshed data**
  - Affected: dashboard `dash_fin_close` (Finance Close Dashboard)
  - Detail: High-criticality dashboard uses manually refreshed datasets: Annual Budget Plan.
  - Recommendation: Move these datasets to scheduled refreshes with freshness alerts and documented SLAs.
- **LINT010: Certified dashboard uses uncertified datasets**
  - Affected: dashboard `card_marketing_roi` (Marketing ROI Snapshot)
  - Detail: Certified dashboard is backed by uncertified datasets: Sales Bookings Pipeline.
  - Recommendation: Certify upstream datasets or remove dashboard certification until dependencies are trusted.

## Medium Findings
- **LINT002: Dataset owner is missing**
  - Affected: dataset `ds_hr_headcount` (Workforce Headcount Planning)
  - Detail: Dataset has no accountable business owner.
  - Recommendation: Assign a business owner responsible for definitions, quality expectations, and escalation.
- **LINT003: Dashboard or card owner is missing**
  - Affected: dashboard `dash_people_plan` (Workforce Planning Overview)
  - Detail: Dashboard/card has no accountable business owner.
  - Recommendation: Assign a business owner who can approve definitions, certification, and remediation decisions.
- **LINT006: Dataset is stale**
  - Affected: dataset `ds_budget_plan` (Annual Budget Plan)
  - Detail: Dataset last refreshed on 2026-01-31 is stale for its manual cadence.
  - Recommendation: Refresh the dataset, correct the cadence metadata, or document why stale data is acceptable.
- **LINT006: Dataset is stale**
  - Affected: dataset `ds_cs_health` (Customer Success Health Scores)
  - Detail: Dataset last refreshed on 2026-05-20 is stale for its weekly cadence.
  - Recommendation: Refresh the dataset, correct the cadence metadata, or document why stale data is acceptable.
- **LINT006: Dataset is stale**
  - Affected: dataset `ds_hr_headcount` (Workforce Headcount Planning)
  - Detail: Dataset last refreshed on 2026-03-31 is stale for its monthly cadence.
  - Recommendation: Refresh the dataset, correct the cadence metadata, or document why stale data is acceptable.
- **LINT006: Dataset is stale**
  - Affected: dataset `ds_product_usage` (Product Usage Telemetry)
  - Detail: Dataset last refreshed on 2026-05-01 is stale for its daily cadence.
  - Recommendation: Refresh the dataset, correct the cadence metadata, or document why stale data is acceptable.

## Low Findings
- **LINT009: High-row-count dataset has low usage**
  - Affected: dataset `ds_ops_fulfillment` (Operations Fulfillment Events)
  - Detail: Dataset has 9,400,000 rows but low usage.
  - Recommendation: Review whether this dataset should be archived, summarized, promoted, or redesigned as a governed data product.
- **LINT009: High-row-count dataset has low usage**
  - Affected: dataset `ds_product_usage` (Product Usage Telemetry)
  - Detail: Dataset has 18,800,000 rows but low usage.
  - Recommendation: Review whether this dataset should be archived, summarized, promoted, or redesigned as a governed data product.

## Recommended Fix Order
Fix critical findings first because missing upstream data and sensitive-data stewardship gaps can undermine trust, access control, and executive reporting. Next address high-severity certification, ownership, stale-data, and manual-refresh issues that affect decision-critical dashboards. Then resolve medium and low findings to improve maintainability, reduce clutter, and strengthen long-term governance.

## Notes
Linting is advisory: it reports metadata quality and governance issues, does not modify the source platform, and should not block structural parsing unless the inventory payload itself is malformed.