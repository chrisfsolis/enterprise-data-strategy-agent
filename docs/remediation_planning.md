# Remediation Planning

The remediation planning layer turns metadata review into a practical backlog that an enterprise data manager can use with stakeholders.

## How findings become remediation items

The planner starts with structurally valid inventory metadata, the active strategy policy, lint findings, and the analyzer/scoring result. Each lint finding becomes a `RemediationItem` with a stable ID, title, description, priority, severity, affected asset, owner role, supporting stakeholders, effort estimate, expected impact, time horizon, recommended action, and success measure.

The planner also creates score-gap items when health scores fall below target levels. These items help connect individual metadata issues to broader governance, ownership, freshness, trust, and executive reporting improvement work.

## How priority is assigned

Priority assignment is intentionally simple and explainable:

- Critical findings become P0 or P1 depending on business criticality.
- High findings become P1 or P2.
- Medium findings become P2.
- Low findings become P3.
- Executive reporting issues are promoted because they can affect leadership decisions.
- Sensitive data stewardship issues are promoted because they create governance and compliance risk.
- Missing owners on high-criticality assets are promoted because accountability is required before remediation can proceed.
- Duplicate metric findings become standardization work.
- Stale executive reporting datasets become immediate review work.
- Orphan datasets become rationalization or archival review work.
- Dashboards without datasets become dashboard rationalization review work.

## How effort and impact are estimated

Effort is estimated with three levels:

- `small`: ownership assignment, metadata correction, or a focused stewardship decision.
- `medium`: stale-data review, orphan dataset rationalization, dashboard rationalization, or score-gap remediation.
- `large`: cross-functional metric standardization, certification dependency cleanup, or refresh/SLA redesign.

Impact is estimated with three levels:

- `high`: P0/P1 work, executive reporting work, or sensitive data stewardship work.
- `medium`: most P2 governance and quality improvements.
- `low`: lower-priority cleanup or archival review.

## How enterprise data managers can use the backlog

A data manager can use the backlog to:

- Prepare stakeholder meetings by domain and priority.
- Assign accountable owner roles before technical cleanup starts.
- Sequence immediate, 30-day, 60-day, and 90-day work.
- Track success measures such as certified critical dashboards, owner coverage, stale dataset remediation, duplicate metric reduction, sensitive-data stewardship coverage, and reduction in high/critical lint findings.
- Convert advisory findings into sprint work, governance council agenda items, or BI administration tasks.

## Future workflow integrations

The JSON backlog is designed to be machine-readable so future versions can feed work management or governance systems such as Jira, Asana, ServiceNow, GitHub Issues, or Domo workflows. Possible integrations include creating tickets, routing approvals, linking remediation to certified datasets, and tracking accepted-risk decisions.

## Why advisory planning is safer than automatic remediation

Enterprise analytics assets often support financial reporting, customer operations, executive reviews, compliance processes, and operational decisions. Automatically changing ownership, certification, schedules, permissions, formulas, or dashboard links can break trusted workflows or hide important context. Advisory planning is safer because it keeps humans in control: the agent explains risks and recommended actions, while accountable business and data owners decide what should actually change.
