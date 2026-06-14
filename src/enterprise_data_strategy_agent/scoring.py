"""Scoring utilities for enterprise data strategy health."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from enterprise_data_strategy_agent.config import (
    CRITICALITY_LEVELS,
    EXECUTIVE_AUDIENCE_KEYWORDS,
    EXECUTIVE_DOMAINS,
    EXECUTIVE_REPORTING_RISK_WEIGHT,
    FRESHNESS_MANUAL_REFRESH_PENALTY,
    FRESHNESS_STALE_WEIGHT,
    GOVERNANCE_MANUAL_REFRESH_PENALTY,
    GOVERNANCE_SENSITIVE_WITHOUT_STEWARD_PENALTY,
    GOVERNANCE_UNCERTIFIED_WEIGHT,
    HIGH_SENSITIVITY,
    OWNERSHIP_MISSING_OWNER_WEIGHT,
    OWNERSHIP_SENSITIVE_WITHOUT_STEWARD_PENALTY,
    TRUST_SCORE_WEIGHTS,
)
from enterprise_data_strategy_agent.policy import DEFAULT_POLICY, StrategyPolicy
from enterprise_data_strategy_agent.models import Dashboard, Dataset, Inventory


@dataclass(frozen=True)
class HealthScores:
    """Scorecard from 0 to 100, where higher is healthier."""

    overall: int
    governance: int
    trust: int
    freshness: int
    ownership: int
    executive_reporting_risk: int


@dataclass(frozen=True)
class ScoreFactor:
    """A contributing scoring adjustment."""

    name: str
    points: float
    rationale: str


@dataclass(frozen=True)
class ScoreExplanation:
    """Human-readable explanation for a health score."""

    score_name: str
    base_score: float
    penalties_or_bonuses: list[ScoreFactor] = field(default_factory=list)
    final_score: int = 0
    rationale: str = ""


def is_stale(dataset: Dataset, as_of: date, policy: StrategyPolicy | None = None) -> bool:
    """Return True when a dataset is beyond the expected freshness window."""

    active_policy = policy or DEFAULT_POLICY
    threshold = active_policy.freshness_thresholds.for_cadence(dataset.refresh_cadence)
    return (as_of - dataset.last_refreshed).days > threshold


def clamp(value: float) -> int:
    """Clamp a numeric score to the 0-100 range."""

    return max(0, min(100, round(value)))


def calculate_scores(inventory: Inventory, policy: StrategyPolicy | None = None) -> HealthScores:
    """Calculate enterprise strategy health scores from metadata signals."""

    scores, _ = _calculate_scorecard(inventory, policy or DEFAULT_POLICY)
    return scores


def explain_scores(inventory: Inventory, policy: StrategyPolicy | None = None) -> dict[str, ScoreExplanation]:
    """Calculate health scores and return detailed scoring explanations."""

    _, explanations = _calculate_scorecard(inventory, policy or DEFAULT_POLICY)
    return explanations


def _calculate_scorecard(inventory: Inventory, policy: StrategyPolicy) -> tuple[HealthScores, dict[str, ScoreExplanation]]:
    datasets = inventory.datasets
    dashboards = inventory.dashboards
    assets = [*datasets, *dashboards]
    total_assets = max(1, len(assets))
    total_datasets = max(1, len(datasets))
    executive_dashboards = [dashboard for dashboard in dashboards if _is_executive(dashboard)]
    total_executive_dashboards = max(1, len(executive_dashboards))

    uncertified = sum(_requires_certification(asset) and not asset.certified for asset in assets)
    missing_owners = sum(not asset.owner for asset in assets)
    stale = sum(is_stale(dataset, inventory.generated_at, policy) for dataset in datasets)
    manual = sum(dataset.refresh_cadence == "manual" for dataset in datasets)
    sensitive_without_steward = sum(dataset.sensitivity_level in HIGH_SENSITIVITY and not dataset.steward for dataset in datasets)

    dataset_by_id = {dataset.id: dataset for dataset in datasets}
    risky_exec = 0
    for dashboard in dashboards:
        related = [dataset_by_id[dataset_id] for dataset_id in dashboard.dataset_ids if dataset_id in dataset_by_id]
        missing_dataset_ids = [dataset_id for dataset_id in dashboard.dataset_ids if dataset_id not in dataset_by_id]
        if _is_executive(dashboard) and (
            not dashboard.certified
            or not dashboard.owner
            or bool(missing_dataset_ids)
            or any(is_stale(dataset, inventory.generated_at, policy) or (policy.risk_thresholds.high_criticality_requires_certified_sources and not dataset.certified) for dataset in related)
        ):
            risky_exec += 1

    governance_factors = [
        ScoreFactor("Uncertified expected assets", -(uncertified / total_assets) * GOVERNANCE_UNCERTIFIED_WEIGHT, f"{uncertified} assets that require certification are not certified."),
        ScoreFactor("Sensitive datasets without stewards", -sensitive_without_steward * GOVERNANCE_SENSITIVE_WITHOUT_STEWARD_PENALTY, f"{sensitive_without_steward} high-sensitivity datasets lack a named steward."),
        ScoreFactor("Manual refresh cadence", -manual * GOVERNANCE_MANUAL_REFRESH_PENALTY, f"{manual} datasets use manual refreshes, which weakens repeatable governance."),
    ]
    governance = _final_from_factors(100, governance_factors)

    ownership_factors = [
        ScoreFactor("Missing owners", -(missing_owners / total_assets) * OWNERSHIP_MISSING_OWNER_WEIGHT, f"{missing_owners} assets are missing business owners."),
        ScoreFactor("Sensitive stewardship gaps", -sensitive_without_steward * OWNERSHIP_SENSITIVE_WITHOUT_STEWARD_PENALTY, f"{sensitive_without_steward} sensitive datasets have no steward assigned."),
    ]
    ownership = _final_from_factors(100, ownership_factors)

    freshness_factors = [
        ScoreFactor("Stale datasets", -(stale / total_datasets) * FRESHNESS_STALE_WEIGHT, f"{stale} of {len(datasets)} datasets exceed configured stale-data windows."),
        ScoreFactor("Manual refresh cadence", -manual * FRESHNESS_MANUAL_REFRESH_PENALTY, f"{manual} datasets rely on manual refreshes rather than automated freshness controls."),
    ]
    freshness = _final_from_factors(100, freshness_factors)

    trust_factors = [
        ScoreFactor("Governance contribution", governance * TRUST_SCORE_WEIGHTS["governance"], f"Governance contributes {TRUST_SCORE_WEIGHTS['governance']:.0%} of trust."),
        ScoreFactor("Freshness contribution", freshness * TRUST_SCORE_WEIGHTS["freshness"], f"Freshness contributes {TRUST_SCORE_WEIGHTS['freshness']:.0%} of trust."),
        ScoreFactor("Ownership contribution", ownership * TRUST_SCORE_WEIGHTS["ownership"], f"Ownership contributes {TRUST_SCORE_WEIGHTS['ownership']:.0%} of trust."),
    ]
    trust = _final_from_factors(0, trust_factors)

    executive_factors = [
        ScoreFactor("Risky executive dashboards", -(risky_exec / total_executive_dashboards) * EXECUTIVE_REPORTING_RISK_WEIGHT, f"{risky_exec} of {len(executive_dashboards)} executive or critical dashboards have certification, owner, or upstream data risks."),
    ]
    executive = _final_from_factors(100, executive_factors)

    overall_factors = [
        ScoreFactor("Governance", governance * policy.scoring_weights.normalized()["governance"], f"Governance contributes {policy.scoring_weights.normalized()['governance']:.0%} of the overall score."),
        ScoreFactor("Trust", trust * policy.scoring_weights.normalized()["trust"], f"Trust contributes {policy.scoring_weights.normalized()['trust']:.0%} of the overall score."),
        ScoreFactor("Freshness", freshness * policy.scoring_weights.normalized()["freshness"], f"Freshness contributes {policy.scoring_weights.normalized()['freshness']:.0%} of the overall score."),
        ScoreFactor("Ownership", ownership * policy.scoring_weights.normalized()["ownership"], f"Ownership contributes {policy.scoring_weights.normalized()['ownership']:.0%} of the overall score."),
        ScoreFactor("Executive reporting risk", executive * policy.scoring_weights.normalized()["executive_reporting_risk"], f"Executive reporting risk contributes {policy.scoring_weights.normalized()['executive_reporting_risk']:.0%} of the overall score."),
    ]
    overall = _final_from_factors(0, overall_factors)

    scores = HealthScores(overall, governance, trust, freshness, ownership, executive)
    explanations = {
        "overall": _explain("overall", 0, overall_factors, overall),
        "governance": _explain("governance", 100, governance_factors, governance),
        "trust": _explain("trust", 0, trust_factors, trust),
        "freshness": _explain("freshness", 100, freshness_factors, freshness),
        "ownership": _explain("ownership", 100, ownership_factors, ownership),
        "executive_reporting_risk": _explain("executive_reporting_risk", 100, executive_factors, executive),
    }
    return scores, explanations


def _final_from_factors(base_score: float, factors: list[ScoreFactor]) -> int:
    return clamp(base_score + sum(factor.points for factor in factors))


def _explain(score_name: str, base_score: float, factors: list[ScoreFactor], final_score: int) -> ScoreExplanation:
    drivers = [factor.rationale for factor in factors if factor.points]
    rationale = " ".join(drivers) if drivers else "No negative scoring signals were detected for this score."
    return ScoreExplanation(score_name, base_score, factors, final_score, rationale)


def _requires_certification(asset: Dataset | Dashboard) -> bool:
    return asset.business_domain in {"Executive Reporting", "Finance"} or asset.business_criticality in CRITICALITY_LEVELS


def _is_executive(dashboard: Dashboard) -> bool:
    return (
        dashboard.business_domain in EXECUTIVE_DOMAINS
        or any(keyword in dashboard.audience.lower() for keyword in EXECUTIVE_AUDIENCE_KEYWORDS)
        or dashboard.business_criticality in CRITICALITY_LEVELS
    )
