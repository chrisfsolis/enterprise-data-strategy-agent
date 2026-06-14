"""Markdown report generation."""

from __future__ import annotations

from enterprise_data_strategy_agent.analyzer import AnalysisResult
from enterprise_data_strategy_agent.models import Inventory

DISCLAIMER = "This project is independent and is not affiliated with, endorsed by, or sponsored by Domo. Domo-style metadata is used only as the first reference implementation."


def generate_markdown_report(inventory: Inventory, analysis: AnalysisResult) -> str:
    """Generate a consultant-style enterprise data strategy brief."""

    s = analysis.scores
    lines = [
        "# Enterprise Data Strategy Brief",
        "",
        "## Executive Summary",
        f"The analytics environment shows an overall health score of {s.overall}/100. The strongest immediate opportunities are to improve ownership, certify executive reporting paths, remediate stale datasets, and standardize duplicate metric logic before it reaches business-critical dashboards.",
        "",
        "## Platform Context",
        f"This version analyzes synthetic metadata from the {inventory.platform} for datasets, cards, dashboards, owners, certification, calculated metrics, sensitivity, usage, and refresh patterns. {DISCLAIMER}",
        "",
        "## Health Scores",
        *_score_lines(analysis),
        "",
        "## Top Findings",
        *_bullets(analysis.top_risks),
        "",
        "## Governance Gaps",
        *_bullets(analysis.governance_improvements),
        "",
        "## Data Quality and Trust Issues",
        "Strategic trust findings below are generated separately from the metadata-quality lint results that follow.",
        *_bullets([*(f"Stale dataset: {name}" for name in analysis.stale_datasets), *(f"Duplicate metric candidate: {name}" for name in analysis.duplicate_metrics), "Manual refreshes and inconsistent calculation names should be treated as trust risks, not only operational cleanup."]),
        "",
        "## Metadata Lint Summary",
        *_lint_summary_lines(analysis),
        "",
        "## Metadata Quality Lint Findings",
        *_lint_detail_lines(analysis),
        "",
        "## Dashboard and Reporting Risk",
        *_bullets(analysis.risky_dashboards or ["No critical dashboard risks were detected in the sample inventory."]),
        "",
        "## Trusted Data Product Opportunities",
        *_bullets(analysis.trusted_data_products[:5]),
        "",
        "## Recommended 30/60/90 Day Plan",
        *_plan(analysis.actions_30_60_90),
        "",
        "## Domo-Oriented Recommendations",
        "Use certified datasets for executive paths, assign card and dashboard owners, standardize Beast Mode-style calculations, rationalize overlapping dashboards, configure alerts for freshness exceptions, route certification through governance workflows, and review metadata on a recurring cadence.",
        "",
        "## Future Platform Opportunities",
        "The same pattern can expand to Snowflake, Tableau, Power BI, Looker, dbt, Collibra, Alation, Atlan, and other analytics or governance systems by implementing additional read-only metadata connectors.",
        "",
        "## Next Steps",
        *_bullets(analysis.quick_wins),
        "",
        "## Suggested Stakeholder Conversations",
        *_bullets(analysis.stakeholder_conversations),
        "",
    ]
    return "\n".join(lines)


def _bullets(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items]


def _plan(plan: dict[str, list[str]]) -> list[str]:
    lines: list[str] = []
    for period, items in plan.items():
        lines.append(f"### {period}")
        lines.extend(_bullets(items))
    return lines


def _score_lines(analysis: AnalysisResult) -> list[str]:
    labels = {
        "overall": "Overall enterprise data strategy health",
        "governance": "Governance score",
        "trust": "Trust score",
        "freshness": "Freshness score",
        "ownership": "Ownership score",
        "executive_reporting_risk": "Executive reporting risk score",
    }
    lines: list[str] = []
    for name, label in labels.items():
        score = getattr(analysis.scores, name)
        explanation = analysis.score_explanations.get(name)
        lines.append(f"- {label}: **{score}/100**")
        if explanation:
            lines.append(f"  - Why: {explanation.rationale}")
            material_factors = [factor for factor in explanation.penalties_or_bonuses if factor.points]
            for factor in material_factors:
                direction = "bonus" if factor.points > 0 else "penalty"
                lines.append(f"  - {factor.name}: {direction} {factor.points:+.1f} points — {factor.rationale}")
    return lines


def _lint_summary_lines(analysis: AnalysisResult) -> list[str]:
    if not analysis.lint_findings:
        return ["- No metadata lint findings were detected."]
    severities = ("critical", "high", "medium", "low")
    counts = {severity: sum(1 for finding in analysis.lint_findings if finding.severity == severity) for severity in severities}
    lines = [
        f"- Total lint findings: **{len(analysis.lint_findings)}**",
        *(f"- {severity.title()}: **{counts[severity]}**" for severity in severities),
    ]
    lines.append("- Highest-priority examples:")
    for finding in analysis.lint_findings[:5]:
        lines.append(f"  - **{finding.severity.upper()} {finding.rule_id}** {finding.affected_object_type} `{finding.affected_object_id}`: {finding.title}. Recommendation: {finding.recommendation}")
    return lines


def _lint_detail_lines(analysis: AnalysisResult) -> list[str]:
    if not analysis.lint_findings:
        return ["- No metadata-quality lint findings were detected."]
    return [
        f"- **{finding.severity.upper()} {finding.rule_id}** {finding.affected_object_type} `{finding.affected_object_id}`: {finding.description} Recommended action: {finding.recommendation}"
        for finding in analysis.lint_findings
    ]
