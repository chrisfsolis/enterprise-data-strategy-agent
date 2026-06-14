"""Analysis engine for enterprise analytics metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations

from enterprise_data_strategy_agent.config import CRITICALITY_LEVELS, HIGH_SENSITIVITY
from enterprise_data_strategy_agent.models import Inventory
from enterprise_data_strategy_agent.scoring import HealthScores, ScoreExplanation, calculate_scores, explain_scores, is_stale
from enterprise_data_strategy_agent.validation import LintFinding, lint_inventory


@dataclass(frozen=True)
class AnalysisResult:
    """Structured findings produced by the analyzer."""

    scores: HealthScores
    score_explanations: dict[str, ScoreExplanation] = field(default_factory=dict)
    top_risks: list[str] = field(default_factory=list)
    quick_wins: list[str] = field(default_factory=list)
    actions_30_60_90: dict[str, list[str]] = field(default_factory=dict)
    trusted_data_products: list[str] = field(default_factory=list)
    governance_improvements: list[str] = field(default_factory=list)
    stakeholder_conversations: list[str] = field(default_factory=list)
    risky_dashboards: list[str] = field(default_factory=list)
    stale_datasets: list[str] = field(default_factory=list)
    duplicate_metrics: list[str] = field(default_factory=list)
    lint_findings: list[LintFinding] = field(default_factory=list)


def analyze_inventory(inventory: Inventory) -> AnalysisResult:
    """Analyze metadata and return practical strategy recommendations."""

    scores = calculate_scores(inventory)
    score_explanations = explain_scores(inventory)
    dataset_by_id = {dataset.id: dataset for dataset in inventory.datasets}
    stale_datasets = [dataset.name for dataset in inventory.datasets if is_stale(dataset, inventory.generated_at)]
    missing_owner_assets = [asset.name if hasattr(asset, "name") else asset.title for asset in [*inventory.datasets, *inventory.dashboards] if not asset.owner]
    sensitive_gaps = [dataset.name for dataset in inventory.datasets if dataset.sensitivity_level in HIGH_SENSITIVITY and not dataset.steward]
    duplicate_metrics = _find_duplicate_metrics(inventory)
    lint_findings = lint_inventory(inventory)

    risky_dashboards = []
    for dashboard in inventory.dashboards:
        related = [dataset_by_id[dataset_id] for dataset_id in dashboard.dataset_ids if dataset_id in dataset_by_id]
        missing_dataset_ids = [dataset_id for dataset_id in dashboard.dataset_ids if dataset_id not in dataset_by_id]
        reasons = []
        if not dashboard.certified:
            reasons.append("uncertified")
        if not dashboard.owner:
            reasons.append("missing owner")
        if any(not dataset.certified for dataset in related):
            reasons.append("uses uncertified datasets")
        if any(is_stale(dataset, inventory.generated_at) for dataset in related):
            reasons.append("powered by stale data")
        if missing_dataset_ids:
            reasons.append(f"references missing datasets: {', '.join(missing_dataset_ids)}")
        if reasons and (dashboard.business_criticality in CRITICALITY_LEVELS or "executive" in dashboard.audience.lower()):
            risky_dashboards.append(f"{dashboard.title}: {', '.join(reasons)}")

    top_risks = []
    if stale_datasets:
        top_risks.append(f"{len(stale_datasets)} datasets are stale, including {', '.join(stale_datasets[:3])}.")
    if risky_dashboards:
        top_risks.append(f"{len(risky_dashboards)} executive or critical dashboards have reporting risk.")
    if missing_owner_assets:
        top_risks.append(f"{len(missing_owner_assets)} assets are missing clear business owners.")
    if duplicate_metrics:
        top_risks.append("Revenue-related metrics appear duplicated or inconsistently named across datasets.")
    if sensitive_gaps:
        top_risks.append(f"Sensitive datasets lack named stewardship: {', '.join(sensitive_gaps)}.")

    quick_wins = [
        "Assign owners to high-usage dashboards and critical datasets with missing accountability.",
        "Certify executive dashboards only after upstream datasets meet freshness and ownership expectations.",
        "Create a shared revenue metric definition and retire duplicate Beast Mode-style calculations.",
        "Move manually refreshed critical datasets onto documented schedules or alerts.",
    ]

    actions = {
        "30 days": [
            "Confirm owners, stewards, and business criticality for every executive reporting asset.",
            "Triage stale and manually refreshed datasets that feed critical dashboards.",
            "Document standard definitions for revenue, churn, pipeline, and active customer metrics.",
        ],
        "60 days": [
            "Create certified domain datasets for Finance, Sales, Customer Success, and Executive Reporting.",
            "Rationalize duplicate cards and dashboards with overlapping KPI logic.",
            "Introduce metadata review ceremonies for ownership, sensitivity, and certification changes.",
        ],
        "90 days": [
            "Launch trusted data product scorecards with owners, SLAs, definitions, and known limitations.",
            "Automate freshness and certification exception reporting.",
            "Prepare a read-only connector roadmap for live platform metadata ingestion.",
        ],
    }

    products = [
        "Executive KPI Certified Data Product",
        "Finance Revenue and Bookings Data Product",
        "Sales Pipeline and Forecast Data Product",
        "Customer Health and Renewal Data Product",
        "Operations Fulfillment and SLA Data Product",
    ]
    improvements = [
        "Require owners and stewards for certified and sensitive datasets.",
        "Separate experimental dashboards from certified executive reporting surfaces.",
        "Standardize calculated metric naming, definitions, and approval workflow.",
        "Review high-row-count, low-usage datasets for archiving or data product redesign.",
    ]
    conversations = [
        "Meet Finance and Sales leaders to align on revenue metric definitions.",
        "Meet executive reporting owners to agree on certification standards and escalation paths.",
        "Meet BI administrators to design recurring metadata quality reviews.",
        "Meet security and governance owners to clarify stewardship for sensitive data.",
    ]

    return AnalysisResult(scores, score_explanations, top_risks, quick_wins, actions, products, improvements, conversations, risky_dashboards, stale_datasets, duplicate_metrics, lint_findings)


def _find_duplicate_metrics(inventory: Inventory) -> list[str]:
    metrics = [metric for dataset in inventory.datasets for metric in dataset.calculated_metrics]
    duplicates: list[str] = []
    for left, right in combinations(metrics, 2):
        if "revenue" in left.name.lower() and "revenue" in right.name.lower() and left.expression.replace(" ", "").lower() == right.expression.replace(" ", "").lower():
            duplicates.append(f"{left.name} and {right.name}")
    return duplicates
