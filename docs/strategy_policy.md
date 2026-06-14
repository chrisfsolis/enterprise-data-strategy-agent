# Strategy Policy Configuration

The strategy policy file lets enterprise data managers tune the Enterprise Data Strategy Agent for their organization's governance model instead of relying on one hardcoded set of assumptions.

## What the policy file controls

`config/sample_strategy_policy.yml` controls:

- Organization context: name, industry, maturity stage, primary platform, and strategy owner role.
- Freshness thresholds for daily, weekly, monthly, and manually refreshed datasets.
- Usage thresholds such as high-row-count and low/high usage expectations.
- Risk expectations for executive certification, sensitive data ownership, stewardship, and certified critical sources.
- Scoring weights across governance, trust, freshness, ownership, and executive reporting risk.
- Severity overrides for key metadata lint findings.
- Trusted data product domains recommended in the strategy brief.
- Stakeholder roles to include in recommended conversations.

## Why hardcoded governance assumptions are risky

Hardcoded assumptions make every organization look as if it has the same risk appetite. That is rarely true. A public company preparing board reporting may require daily executive KPIs to refresh within two days and may treat uncertified executive sources as critical. A smaller private company may accept weekly refreshes and lighter certification while it is still building governance muscle.

When assumptions live in code, enterprise data managers cannot easily explain, approve, or change them. A policy file makes those assumptions explicit, reviewable, and version-controlled.

## How enterprise data managers should tune thresholds

Start by mapping thresholds to business impact:

1. Identify dashboards used for executive, financial, compliance, or customer-impacting decisions.
2. Decide acceptable stale-data windows by refresh cadence and decision frequency.
3. Set ownership and stewardship requirements for sensitive or regulated data.
4. Calibrate severity overrides so lint reports match internal escalation norms.
5. Tune scoring weights to reflect current priorities, such as improving ownership before optimizing freshness.
6. Review generated reports with stakeholders and adjust the policy as governance matures.

## Example settings for a smaller company

A smaller company may want pragmatic defaults while ownership is still forming:

```yaml
freshness_thresholds:
  daily_dataset_stale_after_days: 5
  weekly_dataset_stale_after_days: 21
  monthly_dataset_stale_after_days: 60
  manual_dataset_review_after_days: 45

scoring_weights:
  governance: 0.20
  trust: 0.25
  freshness: 0.20
  ownership: 0.25
  executive_reporting_risk: 0.10

severity_overrides:
  stale_dataset: medium
  missing_dataset_owner: medium
```

## Example settings for a mature enterprise

A mature enterprise may use stricter thresholds and higher executive-reporting escalation:

```yaml
freshness_thresholds:
  daily_dataset_stale_after_days: 2
  weekly_dataset_stale_after_days: 10
  monthly_dataset_stale_after_days: 35
  manual_dataset_review_after_days: 14

risk_thresholds:
  executive_dashboard_minimum_certification_required: true
  sensitive_data_requires_owner: true
  sensitive_data_requires_steward: true
  high_criticality_requires_certified_sources: true

severity_overrides:
  executive_dashboard_uncertified_source: critical
  sensitive_dataset_without_owner: critical
  stale_dataset: high
```

## Future platform support

The policy layer is intentionally platform-neutral. Today the sample inventory uses Domo-style metadata, but the same thresholds and assumptions can apply to metadata from Snowflake, Tableau, Power BI, Looker, dbt, Collibra, Alation, Atlan, or other systems. Future connectors can normalize platform metadata into the existing inventory model while the policy continues to define organization-specific governance expectations.
