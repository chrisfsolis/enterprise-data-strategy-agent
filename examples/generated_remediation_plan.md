# Enterprise Data Remediation Plan

## Executive Summary
The remediation backlog contains 28 advisory work items, including 19 P0/P1 actions. Fix executive reporting trust first because these issues have the highest potential to affect executive trust, sensitive-data stewardship, ownership accountability, and operational decision-making. Recommended first action: Certify upstream datasets or clearly label the dashboard as not certified for executive decision-making.

## Policy Context
- Organization name: Acme Enterprise
- Primary platform: Domo
- Maturity stage: Governed self-service analytics
- Custom policy used: yes

## Remediation Backlog Summary
- Total remediation items: **28**
- By Priority: P0=7, P1=12, P2=7, P3=2
- By Severity: critical=6, high=12, medium=8, low=2
- By Effort: small=12, medium=12, large=4
- By Time Horizon: immediate=12, 30_days=7, 60_days=7, 90_days=2, later=0

## P0 Immediate Actions
- **REM-001: Executive dashboard uses uncertified datasets** (critical, Executive Reporting, small effort) — Certify upstream datasets or clearly label the dashboard as not certified for executive decision-making. Success measure: Finding is resolved or accepted with documented business rationale.
- **REM-002: Executive dashboard uses uncertified datasets** (critical, Executive Reporting, small effort) — Certify upstream datasets or clearly label the dashboard as not certified for executive decision-making. Success measure: Finding is resolved or accepted with documented business rationale.
- **REM-003: Sensitive dataset lacks stewardship** (critical, Customer Success, small effort) — Assign a data steward responsible for access, definitions, and quality expectations. Success measure: Sensitive datasets with assigned stewardship reaches target coverage.
- **REM-004: Sensitive dataset lacks stewardship** (critical, Executive Reporting, small effort) — Assign both an owner and a steward before broadening access or certification. Success measure: Sensitive datasets with assigned stewardship reaches target coverage.
- **REM-005: Sensitive dataset lacks stewardship** (critical, Operations, small effort) — Assign both an owner and a steward before broadening access or certification. Success measure: Sensitive datasets with assigned stewardship reaches target coverage.
- **REM-006: Sensitive dataset lacks stewardship** (critical, Product, small effort) — Assign a data steward responsible for access, definitions, and quality expectations. Success measure: Sensitive datasets with assigned stewardship reaches target coverage.
- **REM-011: Review and remediate stale dataset** (high, Executive Reporting, medium effort) — Confirm whether the dataset is still required, refresh it, define an SLA, or retire dependent reporting. Success measure: Stale executive or high-criticality datasets remediated or formally retired.

## P1 High Priority Actions
- **REM-007: Dataset owner is missing** (high, Executive Reporting, small effort) — Assign a business owner responsible for definitions, quality expectations, and escalation. Success measure: High-criticality assets with assigned owners reaches target coverage.
- **REM-008: Dataset owner is missing** (high, Operations, small effort) — Assign a business owner responsible for definitions, quality expectations, and escalation. Success measure: High-criticality assets with assigned owners reaches target coverage.
- **REM-009: Review and remediate stale dataset** (high, Finance, medium effort) — Confirm whether the dataset is still required, refresh it, define an SLA, or retire dependent reporting. Success measure: Stale executive or high-criticality datasets remediated or formally retired.
- **REM-010: Review and remediate stale dataset** (high, Customer Success, medium effort) — Confirm whether the dataset is still required, refresh it, define an SLA, or retire dependent reporting. Success measure: Stale executive or high-criticality datasets remediated or formally retired.
- **REM-012: Review and remediate stale dataset** (high, Operations, medium effort) — Confirm whether the dataset is still required, refresh it, define an SLA, or retire dependent reporting. Success measure: Stale executive or high-criticality datasets remediated or formally retired.
- **REM-013: Review and remediate stale dataset** (high, Product, medium effort) — Confirm whether the dataset is still required, refresh it, define an SLA, or retire dependent reporting. Success measure: Stale executive or high-criticality datasets remediated or formally retired.
- **REM-014: Review and remediate stale dataset** (high, Sales, medium effort) — Confirm whether the dataset is still required, refresh it, define an SLA, or retire dependent reporting. Success measure: Stale executive or high-criticality datasets remediated or formally retired.
- **REM-015: Critical dashboard depends on manually refreshed data** (high, Executive Reporting, large effort) — Move these datasets to scheduled refreshes with freshness alerts and documented SLAs. Success measure: Finding is resolved or accepted with documented business rationale.
- **REM-016: Critical dashboard depends on manually refreshed data** (high, Executive Reporting, large effort) — Move these datasets to scheduled refreshes with freshness alerts and documented SLAs. Success measure: Finding is resolved or accepted with documented business rationale.
- **REM-023: Improve overall score** (medium, Enterprise, medium effort) — Review the score explanation, assign accountable owners, and track remediation against the weakest contributing factors. Success measure: Overall score improves to 70/100 or better.
- **REM-026: Improve freshness score** (medium, Enterprise, medium effort) — Review the score explanation, assign accountable owners, and track remediation against the weakest contributing factors. Success measure: Freshness score improves to 70/100 or better.
- **REM-028: Improve executive reporting risk score** (medium, Enterprise, medium effort) — Review the score explanation, assign accountable owners, and track remediation against the weakest contributing factors. Success measure: Executive Reporting Risk score improves to 70/100 or better.

## P2 Medium Priority Actions
- **REM-017: Critical dashboard depends on manually refreshed data** (high, Finance, large effort) — Move these datasets to scheduled refreshes with freshness alerts and documented SLAs. Success measure: Finding is resolved or accepted with documented business rationale.
- **REM-018: Certified dashboard uses uncertified datasets** (high, Sales, large effort) — Certify upstream datasets or remove dashboard certification until dependencies are trusted. Success measure: Finding is resolved or accepted with documented business rationale.
- **REM-019: Dashboard or card owner is missing** (medium, Executive Reporting, small effort) — Assign a business owner who can approve definitions, certification, and remediation decisions. Success measure: High-criticality assets with assigned owners reaches target coverage.
- **REM-020: Dashboard or card owner is missing** (medium, Operations, small effort) — Assign a business owner who can approve definitions, certification, and remediation decisions. Success measure: High-criticality assets with assigned owners reaches target coverage.
- **REM-024: Improve governance score** (medium, Enterprise, medium effort) — Review the score explanation, assign accountable owners, and track remediation against the weakest contributing factors. Success measure: Governance score improves to 70/100 or better.
- **REM-025: Improve trust score** (medium, Enterprise, medium effort) — Review the score explanation, assign accountable owners, and track remediation against the weakest contributing factors. Success measure: Trust score improves to 70/100 or better.
- **REM-027: Improve ownership score** (medium, Enterprise, medium effort) — Review the score explanation, assign accountable owners, and track remediation against the weakest contributing factors. Success measure: Ownership score improves to 70/100 or better.

## P3 Lower Priority Actions
- **REM-021: High-row-count dataset has low usage** (low, Operations, small effort) — Review whether this dataset should be archived, summarized, promoted, or redesigned as a governed data product. Success measure: Finding is resolved or accepted with documented business rationale.
- **REM-022: High-row-count dataset has low usage** (low, Product, small effort) — Review whether this dataset should be archived, summarized, promoted, or redesigned as a governed data product. Success measure: Finding is resolved or accepted with documented business rationale.

## 30/60/90 Day Execution Plan
### Immediate
- REM-001: Executive dashboard uses uncertified datasets (Dashboard Owner)
- REM-002: Executive dashboard uses uncertified datasets (Dashboard Owner)
- REM-003: Sensitive dataset lacks stewardship (Data Governance Owner)
- REM-004: Sensitive dataset lacks stewardship (Data Governance Owner)
- REM-005: Sensitive dataset lacks stewardship (Data Governance Owner)
- REM-006: Sensitive dataset lacks stewardship (Data Governance Owner)
- REM-011: Review and remediate stale dataset (Enterprise Data Manager)
- REM-009: Review and remediate stale dataset (Enterprise Data Manager)
- REM-010: Review and remediate stale dataset (Enterprise Data Manager)
- REM-012: Review and remediate stale dataset (Enterprise Data Manager)
- REM-013: Review and remediate stale dataset (Enterprise Data Manager)
- REM-014: Review and remediate stale dataset (Enterprise Data Manager)
### 30 Days
- REM-007: Dataset owner is missing (Enterprise Data Manager)
- REM-008: Dataset owner is missing (Enterprise Data Manager)
- REM-015: Critical dashboard depends on manually refreshed data (Dashboard Owner)
- REM-016: Critical dashboard depends on manually refreshed data (Dashboard Owner)
- REM-023: Improve overall score (Enterprise Data Manager)
- REM-026: Improve freshness score (Enterprise Data Manager)
- REM-028: Improve executive reporting risk score (Enterprise Data Manager)
### 60 Days
- REM-017: Critical dashboard depends on manually refreshed data (Dashboard Owner)
- REM-018: Certified dashboard uses uncertified datasets (Dashboard Owner)
- REM-019: Dashboard or card owner is missing (Dashboard Owner)
- REM-020: Dashboard or card owner is missing (Dashboard Owner)
- REM-024: Improve governance score (Enterprise Data Manager)
- REM-025: Improve trust score (Enterprise Data Manager)
- REM-027: Improve ownership score (Enterprise Data Manager)
### 90 Days
- REM-021: High-row-count dataset has low usage (Enterprise Data Manager)
- REM-022: High-row-count dataset has low usage (Enterprise Data Manager)
### Later
- No planned items.

## Stakeholder Engagement Plan
- Meet with Customer Success Business Owner to confirm ownership, sequencing, acceptance criteria, and decisions needed for their remediation items.
- Meet with Data Governance Owner to confirm ownership, sequencing, acceptance criteria, and decisions needed for their remediation items.
- Meet with Domo Admin to confirm ownership, sequencing, acceptance criteria, and decisions needed for their remediation items.
- Meet with Enterprise Data Manager to confirm ownership, sequencing, acceptance criteria, and decisions needed for their remediation items.
- Meet with Executive Reporting Business Owner to confirm ownership, sequencing, acceptance criteria, and decisions needed for their remediation items.
- Meet with Executive Sponsor to confirm ownership, sequencing, acceptance criteria, and decisions needed for their remediation items.
- Meet with Finance Business Owner to confirm ownership, sequencing, acceptance criteria, and decisions needed for their remediation items.
- Meet with Operations Business Owner to confirm ownership, sequencing, acceptance criteria, and decisions needed for their remediation items.
- Meet with Product Business Owner to confirm ownership, sequencing, acceptance criteria, and decisions needed for their remediation items.
- Meet with Sales Business Owner to confirm ownership, sequencing, acceptance criteria, and decisions needed for their remediation items.
- Meet with Security or Compliance Partner to confirm ownership, sequencing, acceptance criteria, and decisions needed for their remediation items.

## Success Measures
- Percentage of critical dashboards with certified datasets.
- Percentage of high-criticality datasets with owners.
- Number of duplicate metrics resolved.
- Number of stale executive reporting datasets remediated.
- Number of sensitive datasets with assigned stewardship.
- Reduction in high/critical lint findings.

## Notes
This plan is advisory. It does not modify Domo or any other source platform; data managers should validate recommendations with accountable stakeholders before changing assets, access, schedules, or certification status.