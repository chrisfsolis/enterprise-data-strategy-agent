"""Generate actionable remediation plans from lint and strategy findings."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone

from enterprise_data_strategy_agent.analyzer import AnalysisResult
from enterprise_data_strategy_agent.backlog import RemediationItem, summarize_backlog
from enterprise_data_strategy_agent.config import HIGH_SENSITIVITY
from enterprise_data_strategy_agent.linting import LintFinding
from enterprise_data_strategy_agent.models import Dashboard, Dataset, Inventory
from enterprise_data_strategy_agent.policy import DEFAULT_POLICY, StrategyPolicy

_PRIORITY_RANK = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
_SEVERITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def build_remediation_backlog(inventory: Inventory, analysis: AnalysisResult, policy: StrategyPolicy | None = None) -> list[RemediationItem]:
    """Convert lint findings and score gaps into prioritized remediation work."""

    active_policy = policy or DEFAULT_POLICY
    datasets = {dataset.id: dataset for dataset in inventory.datasets}
    dashboards = {dashboard.id: dashboard for dashboard in inventory.dashboards}
    items = [_item_from_finding(index, finding, datasets, dashboards, active_policy) for index, finding in enumerate(analysis.lint_findings, start=1)]
    score_items = _score_gap_items(len(items) + 1, inventory, analysis, active_policy)
    items.extend(score_items)
    return sorted(items, key=lambda item: (_PRIORITY_RANK[item.priority], _SEVERITY_RANK.get(item.severity, 9), item.id))


def generate_markdown_remediation_plan(inventory: Inventory, analysis: AnalysisResult, policy: StrategyPolicy | None = None) -> str:
    """Render a remediation backlog as an enterprise data manager plan."""

    active_policy = policy or DEFAULT_POLICY
    items = build_remediation_backlog(inventory, analysis, active_policy)
    summary = summarize_backlog(items)
    urgent = [item for item in items if item.priority in {"P0", "P1"}]
    theme = most_urgent_theme(items)
    first_action = recommended_first_action(items)
    lines = [
        "# Enterprise Data Remediation Plan",
        "",
        "## Executive Summary",
        f"The remediation backlog contains {len(items)} advisory work items, including {len(urgent)} P0/P1 actions. Fix {theme.lower()} first because these issues have the highest potential to affect executive trust, sensitive-data stewardship, ownership accountability, and operational decision-making. Recommended first action: {first_action}",
        "",
        "## Policy Context",
        f"- Organization name: {active_policy.organization.name}",
        f"- Primary platform: {active_policy.organization.primary_platform}",
        f"- Maturity stage: {active_policy.organization.data_maturity_stage}",
        f"- Custom policy used: {'yes' if active_policy.source_path else 'no'}",
        "",
        "## Remediation Backlog Summary",
        *_summary_lines(summary),
        "",
        "## P0 Immediate Actions",
        *_items_for_priority(items, "P0"),
        "",
        "## P1 High Priority Actions",
        *_items_for_priority(items, "P1"),
        "",
        "## P2 Medium Priority Actions",
        *_items_for_priority(items, "P2"),
        "",
        "## P3 Lower Priority Actions",
        *_items_for_priority(items, "P3"),
        "",
        "## 30/60/90 Day Execution Plan",
        *_timeline(items),
        "",
        "## Stakeholder Engagement Plan",
        *_stakeholder_plan(items, active_policy),
        "",
        "## Success Measures",
        "- Percentage of critical dashboards with certified datasets.",
        "- Percentage of high-criticality datasets with owners.",
        "- Number of duplicate metrics resolved.",
        "- Number of stale executive reporting datasets remediated.",
        "- Number of sensitive datasets with assigned stewardship.",
        "- Reduction in high/critical lint findings.",
        "",
        "## Notes",
        "This plan is advisory. It does not modify Domo or any other source platform; data managers should validate recommendations with accountable stakeholders before changing assets, access, schedules, or certification status.",
    ]
    return "\n".join(lines)


def generate_json_backlog(inventory: Inventory, analysis: AnalysisResult, policy: StrategyPolicy | None = None) -> str:
    """Generate machine-readable remediation backlog JSON."""

    active_policy = policy or DEFAULT_POLICY
    items = build_remediation_backlog(inventory, analysis, active_policy)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy_context": {
            "organization_name": active_policy.organization.name,
            "primary_platform": active_policy.organization.primary_platform,
            "maturity_stage": active_policy.organization.data_maturity_stage,
            "custom_policy_used": bool(active_policy.source_path),
            "policy_source": active_policy.source_path or "Default policy settings",
        },
        "summary": summarize_backlog(items),
        "remediation_items": [item.to_dict() for item in items],
    }
    return json.dumps(payload, indent=2)


def most_urgent_theme(items: list[RemediationItem]) -> str:
    if not items:
        return "No urgent remediation theme"
    top = items[0]
    if "executive" in top.title.lower() or "executive" in top.affected_domain.lower():
        return "Executive reporting trust"
    if "sensitive" in top.title.lower() or "steward" in top.title.lower():
        return "Sensitive data stewardship"
    if "owner" in top.title.lower():
        return "Ownership accountability"
    if "stale" in top.title.lower():
        return "Freshness and SLA recovery"
    if "metric" in top.title.lower():
        return "Metric standardization"
    return top.source_finding_title


def recommended_first_action(items: list[RemediationItem]) -> str:
    return items[0].recommended_action if items else "No remediation action is currently required."


def _item_from_finding(index: int, finding: LintFinding, datasets: dict[str, Dataset], dashboards: dict[str, Dashboard], policy: StrategyPolicy) -> RemediationItem:
    asset = datasets.get(finding.affected_object_id) if finding.affected_object_type == "dataset" else dashboards.get(finding.affected_object_id)
    domain = getattr(asset, "business_domain", "Enterprise") if asset else "Enterprise"
    criticality = getattr(asset, "business_criticality", "medium") if asset else "medium"
    sensitive = isinstance(asset, Dataset) and asset.sensitivity_level in HIGH_SENSITIVITY
    executive = isinstance(asset, Dashboard) and ("executive" in asset.audience.lower() or "executive" in asset.business_domain.lower())
    priority = _priority_for(finding, criticality, executive, sensitive)
    return RemediationItem(
        id=f"REM-{index:03d}",
        title=_title(finding),
        description=finding.description,
        priority=priority,
        severity=finding.severity,
        affected_domain=domain,
        affected_object_type=finding.affected_object_type,
        affected_object_id=finding.affected_object_id,
        affected_object_name=finding.affected_object_name,
        recommended_owner_role=_owner_role(finding, policy),
        supporting_stakeholders=_stakeholders(finding, policy, domain),
        estimated_effort=_effort(finding),
        expected_impact=_impact(priority, finding, executive, sensitive),
        time_horizon=_horizon(priority, finding),
        source_rule_id=finding.rule_id,
        source_finding_title=finding.title,
        recommended_action=_action(finding),
        success_measure=_success_measure(finding),
    )


def _priority_for(finding: LintFinding, criticality: str, executive: bool, sensitive: bool):
    base = {"critical": 1, "high": 2, "medium": 3, "low": 4}[finding.severity]
    if finding.severity == "critical" and criticality == "critical":
        base = 0
    if executive or sensitive or ("owner" in finding.title.lower() and criticality in {"high", "critical"}):
        base -= 1
    if finding.rule_id == "LINT006" and (executive or criticality == "critical"):
        base -= 1
    return ["P0", "P1", "P2", "P3"][max(0, min(3, base))]


def _title(finding: LintFinding) -> str:
    if finding.rule_id == "LINT008":
        return "Standardize duplicate metric definitions"
    if finding.rule_id == "LINT006":
        return "Review and remediate stale dataset"
    if finding.rule_id == "LINT012":
        return "Rationalize or archive orphan dataset"
    if finding.rule_id == "LINT011":
        return "Rationalize dashboard with no linked datasets"
    return finding.title


def _action(finding: LintFinding) -> str:
    if finding.rule_id == "LINT008":
        return "Run a metric-standardization workshop, select an approved definition, and retire or rename duplicate calculations."
    if finding.rule_id == "LINT006":
        return "Confirm whether the dataset is still required, refresh it, define an SLA, or retire dependent reporting."
    if finding.rule_id == "LINT012":
        return "Meet with the domain owner to decide whether to archive, promote, or connect the dataset to governed reporting."
    if finding.rule_id == "LINT011":
        return "Review whether the dashboard is still used; attach valid datasets or archive the dashboard metadata."
    return finding.recommendation


def _owner_role(finding: LintFinding, policy: StrategyPolicy) -> str:
    if "sensitive" in finding.title.lower():
        return "Data Governance Owner"
    if "dashboard" in finding.affected_object_type:
        return "Dashboard Owner"
    if finding.rule_id == "LINT008":
        return "Metric Owner"
    return policy.organization.strategy_owner_role


def _stakeholders(finding: LintFinding, policy: StrategyPolicy, domain: str) -> list[str]:
    roles = [policy.organization.strategy_owner_role, "Domo Admin"]
    if domain and domain != "Enterprise":
        roles.append(f"{domain} Business Owner")
    if "sensitive" in finding.title.lower():
        roles.append("Security or Compliance Partner")
    if "executive" in finding.title.lower() or domain == "Executive Reporting":
        roles.append("Executive Sponsor")
    return list(dict.fromkeys(roles))


def _effort(finding: LintFinding):
    if finding.rule_id in {"LINT008", "LINT007", "LINT010"}:
        return "large"
    if finding.rule_id in {"LINT006", "LINT011", "LINT012"}:
        return "medium"
    return "small"


def _impact(priority: str, finding: LintFinding, executive: bool, sensitive: bool):
    if priority in {"P0", "P1"} or executive or sensitive:
        return "high"
    if finding.severity == "medium":
        return "medium"
    return "low"


def _horizon(priority: str, finding: LintFinding):
    if priority == "P0" or (finding.rule_id == "LINT006" and finding.severity in {"critical", "high"}):
        return "immediate"
    return {"P1": "30_days", "P2": "60_days", "P3": "90_days"}[priority]


def _success_measure(finding: LintFinding) -> str:
    if finding.rule_id == "LINT008":
        return "Duplicate metric count reduced and one approved metric definition documented."
    if finding.rule_id == "LINT006":
        return "Stale executive or high-criticality datasets remediated or formally retired."
    if "owner" in finding.title.lower():
        return "High-criticality assets with assigned owners reaches target coverage."
    if "sensitive" in finding.title.lower():
        return "Sensitive datasets with assigned stewardship reaches target coverage."
    return "Finding is resolved or accepted with documented business rationale."


def _score_gap_items(start: int, inventory: Inventory, analysis: AnalysisResult, policy: StrategyPolicy) -> list[RemediationItem]:
    items: list[RemediationItem] = []
    for name, score in asdict(analysis.scores).items():
        if score >= 70:
            continue
        priority = "P1" if score < 50 else "P2"
        items.append(RemediationItem(f"REM-{start + len(items):03d}", f"Improve {name.replace('_', ' ')} score", f"The {name.replace('_', ' ')} score is {score}/100 and needs management attention.", priority, "medium", "Enterprise", "score", name, name.replace('_', ' ').title(), policy.organization.strategy_owner_role, [policy.organization.strategy_owner_role, "Data Governance Owner"], "medium", "high" if priority == "P1" else "medium", "30_days" if priority == "P1" else "60_days", "SCORE", f"{name} score gap", "Review the score explanation, assign accountable owners, and track remediation against the weakest contributing factors.", f"{name.replace('_', ' ').title()} score improves to 70/100 or better."))
    return items


def _summary_lines(summary: dict[str, dict[str, int] | int]) -> list[str]:
    lines = [f"- Total remediation items: **{summary['total_items']}**"]
    for label in ("by_priority", "by_severity", "by_effort", "by_time_horizon"):
        values = summary[label]
        assert isinstance(values, dict)
        lines.append(f"- {label.replace('_', ' ').title()}: " + ", ".join(f"{key}={value}" for key, value in values.items()))
    return lines


def _items_for_priority(items: list[RemediationItem], priority: str) -> list[str]:
    selected = [item for item in items if item.priority == priority]
    if not selected:
        return ["- No actions in this priority band."]
    return [f"- **{item.id}: {item.title}** ({item.severity}, {item.affected_domain}, {item.estimated_effort} effort) — {item.recommended_action} Success measure: {item.success_measure}" for item in selected]


def _timeline(items: list[RemediationItem]) -> list[str]:
    labels = {"immediate": "Immediate", "30_days": "30 Days", "60_days": "60 Days", "90_days": "90 Days", "later": "Later"}
    lines: list[str] = []
    for horizon, label in labels.items():
        lines.append(f"### {label}")
        selected = [item for item in items if item.time_horizon == horizon]
        lines.extend([f"- {item.id}: {item.title} ({item.recommended_owner_role})" for item in selected] or ["- No planned items."])
    return lines


def _stakeholder_plan(items: list[RemediationItem], policy: StrategyPolicy) -> list[str]:
    stakeholders = sorted({role for item in items for role in item.supporting_stakeholders}) or policy.stakeholder_roles
    return [f"- Meet with {role} to confirm ownership, sequencing, acceptance criteria, and decisions needed for their remediation items." for role in stakeholders]
