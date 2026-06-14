"""UI helpers for the Enterprise Data Strategy Agent Streamlit app."""

from __future__ import annotations

import json
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from enterprise_data_strategy_agent.analyzer import AnalysisResult, analyze_inventory
from enterprise_data_strategy_agent.backlog import RemediationItem, summarize_backlog
from enterprise_data_strategy_agent.linting import LintFinding, generate_markdown_lint_report, lint_inventory
from enterprise_data_strategy_agent.models import Inventory, validate_inventory_payload
from enterprise_data_strategy_agent.planning import build_remediation_backlog, generate_json_backlog, generate_markdown_remediation_plan
from enterprise_data_strategy_agent.policy import DEFAULT_POLICY, StrategyPolicy, load_policy
from enterprise_data_strategy_agent.report import generate_markdown_report
from enterprise_data_strategy_agent.sample_loader import load_sample_inventory

SAMPLE_INVENTORY_PATH = Path("data/sample_domo_inventory.json")
SAMPLE_POLICY_PATH = Path("config/sample_strategy_policy.yml")

SCORE_LABELS = {
    "overall": "Overall",
    "governance": "Governance",
    "trust": "Trust",
    "freshness": "Freshness",
    "ownership": "Ownership",
    "executive_reporting_risk": "Executive reporting risk",
}


@dataclass(frozen=True)
class ReportArtifacts:
    """Generated report and download artifacts for the UI."""

    inventory: Inventory
    policy: StrategyPolicy
    lint_findings: list[LintFinding]
    analysis: AnalysisResult
    remediation_items: list[RemediationItem]
    strategy_brief_markdown: str
    lint_report_markdown: str
    remediation_plan_markdown: str
    remediation_backlog_json: str


def parse_inventory_json(raw_json: str | bytes) -> Inventory:
    """Parse raw inventory JSON text and validate it into an Inventory."""

    if isinstance(raw_json, bytes):
        raw_json = raw_json.decode("utf-8")
    payload = json.loads(raw_json)
    if not isinstance(payload, dict):
        raise ValueError("Inventory JSON must be an object at the top level")
    return validate_inventory_payload(payload)


def load_bundled_sample_inventory(path: str | Path = SAMPLE_INVENTORY_PATH) -> Inventory:
    """Load the bundled synthetic Domo-style inventory."""

    return load_sample_inventory(path)


def load_bundled_sample_policy(path: str | Path = SAMPLE_POLICY_PATH) -> StrategyPolicy:
    """Load the bundled sample strategy policy."""

    return load_policy(path)


def parse_policy_yaml(raw_yaml: str | bytes, source_name: str = "Uploaded policy") -> StrategyPolicy:
    """Parse uploaded policy YAML using the existing policy loader."""

    if isinstance(raw_yaml, bytes):
        raw_yaml = raw_yaml.decode("utf-8")
    with tempfile.NamedTemporaryFile("w", suffix=".yml", encoding="utf-8", delete=False) as handle:
        handle.write(raw_yaml)
        temp_path = Path(handle.name)
    try:
        policy = load_policy(temp_path)
        return StrategyPolicy(**{**policy.__dict__, "source_path": source_name})
    finally:
        temp_path.unlink(missing_ok=True)


def build_report_bundle(inventory: Inventory, policy: StrategyPolicy | None = None) -> tuple[AnalysisResult, str]:
    """Run analysis and generate the markdown strategy brief for a validated inventory."""

    active_policy = policy or DEFAULT_POLICY
    analysis = analyze_inventory(inventory, active_policy)
    return analysis, generate_markdown_report(inventory, analysis, active_policy)


def generate_report_artifacts(inventory: Inventory, policy: StrategyPolicy | None = None) -> ReportArtifacts:
    """Generate all report artifacts used by Streamlit download buttons."""

    active_policy = policy or DEFAULT_POLICY
    lint_findings = lint_inventory(inventory, active_policy)
    analysis = analyze_inventory(inventory, active_policy)
    remediation_items = build_remediation_backlog(inventory, analysis, active_policy)
    return ReportArtifacts(
        inventory=inventory,
        policy=active_policy,
        lint_findings=lint_findings,
        analysis=analysis,
        remediation_items=remediation_items,
        strategy_brief_markdown=generate_markdown_report(inventory, analysis, active_policy),
        lint_report_markdown=generate_markdown_lint_report(inventory, lint_findings, active_policy),
        remediation_plan_markdown=generate_markdown_remediation_plan(inventory, analysis, active_policy),
        remediation_backlog_json=generate_json_backlog(inventory, analysis, active_policy),
    )


def format_score_rows(analysis: AnalysisResult) -> list[dict[str, Any]]:
    """Return health scores in a table-friendly shape for UI rendering."""

    rows: list[dict[str, Any]] = []
    for key, label in SCORE_LABELS.items():
        explanation = analysis.score_explanations.get(key)
        rows.append({"Score": label, "Value": getattr(analysis.scores, key), "Why": explanation.rationale if explanation else "No explanation available."})
    return rows


def summarize_inventory(inventory: Inventory) -> dict[str, Any]:
    """Return compact inventory metadata for display."""

    domains = sorted({asset.business_domain for asset in [*inventory.datasets, *inventory.dashboards] if asset.business_domain})
    sensitive_levels = {"confidential", "restricted", "pii", "phi", "pci"}
    return {
        "Platform": inventory.platform,
        "Generated at": inventory.generated_at.isoformat(),
        "Datasets": len(inventory.datasets),
        "Dashboards/cards": len(inventory.dashboards),
        "Business domains": ", ".join(domains) if domains else "None provided",
        "Certified datasets": sum(1 for dataset in inventory.datasets if dataset.certified),
        "Uncertified datasets": sum(1 for dataset in inventory.datasets if not dataset.certified),
        "Sensitive datasets": sum(1 for dataset in inventory.datasets if dataset.sensitivity_level in sensitive_levels),
        "Executive dashboards/cards": sum(1 for dashboard in inventory.dashboards if "executive" in dashboard.audience.lower() or "executive" in dashboard.business_domain.lower()),
    }


def summarize_policy(policy: StrategyPolicy) -> dict[str, str]:
    """Return user-facing policy context."""

    return {
        "Organization name": policy.organization.name,
        "Industry": policy.organization.industry,
        "Data maturity stage": policy.organization.data_maturity_stage,
        "Primary platform": policy.organization.primary_platform,
        "Strategy owner role": policy.organization.strategy_owner_role,
    }


def finding_rows(findings: list[LintFinding]) -> list[dict[str, str]]:
    """Format lint findings for browser tables."""

    return [{"severity": f.severity, "rule_id": f.rule_id, "affected object name": f.affected_object_name, "affected object type": f.affected_object_type, "title": f.title, "recommendation": f.recommendation} for f in findings]


def remediation_rows(items: list[RemediationItem]) -> list[dict[str, str]]:
    """Format remediation items for browser tables."""

    return [{"priority": i.priority, "title": i.title, "affected domain": i.affected_domain, "recommended owner role": i.recommended_owner_role, "estimated effort": i.estimated_effort, "expected impact": i.expected_impact, "time horizon": i.time_horizon, "recommended action": i.recommended_action, "success measure": i.success_measure} for i in items]


def count_by_severity(findings: list[LintFinding]) -> dict[str, int]:
    """Count lint findings by severity."""

    counts = Counter(f.severity for f in findings)
    return {severity: counts.get(severity, 0) for severity in ("critical", "high", "medium", "low")}


def backlog_summary(items: list[RemediationItem]) -> dict[str, dict[str, int] | int]:
    """Summarize remediation backlog dimensions for display."""

    return summarize_backlog(items)
