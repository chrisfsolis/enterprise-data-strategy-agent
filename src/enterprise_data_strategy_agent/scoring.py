"""Scoring utilities for enterprise data strategy health."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from enterprise_data_strategy_agent.config import STALE_DAYS_BY_CADENCE
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


def is_stale(dataset: Dataset, as_of: date) -> bool:
    """Return True when a dataset is beyond the expected freshness window."""

    threshold = STALE_DAYS_BY_CADENCE.get(dataset.refresh_cadence, 14)
    return (as_of - dataset.last_refreshed).days > threshold


def clamp(value: float) -> int:
    """Clamp a numeric score to the 0-100 range."""

    return max(0, min(100, round(value)))


def calculate_scores(inventory: Inventory) -> HealthScores:
    """Calculate enterprise strategy health scores from metadata signals."""

    datasets = inventory.datasets
    dashboards = inventory.dashboards
    total_assets = max(1, len(datasets) + len(dashboards))
    uncertified = sum(not asset.certified for asset in [*datasets, *dashboards])
    missing_owners = sum(not asset.owner for asset in [*datasets, *dashboards])
    stale = sum(is_stale(dataset, inventory.generated_at) for dataset in datasets)
    manual = sum(dataset.refresh_cadence == "manual" for dataset in datasets)
    sensitive_without_steward = sum(
        dataset.sensitivity_level in {"confidential", "restricted"} and not dataset.steward
        for dataset in datasets
    )
    dataset_by_id = {dataset.id: dataset for dataset in datasets}
    risky_exec = 0
    for dashboard in dashboards:
        related = [dataset_by_id[dataset_id] for dataset_id in dashboard.dataset_ids]
        if _is_executive(dashboard) and (
            not dashboard.certified or not dashboard.owner or any(is_stale(dataset, inventory.generated_at) or not dataset.certified for dataset in related)
        ):
            risky_exec += 1

    governance = clamp(100 - (uncertified / total_assets) * 35 - sensitive_without_steward * 8 - manual * 4)
    ownership = clamp(100 - (missing_owners / total_assets) * 70 - sensitive_without_steward * 6)
    freshness = clamp(100 - (stale / max(1, len(datasets))) * 75 - manual * 3)
    trust = clamp((governance * 0.45) + (freshness * 0.35) + (ownership * 0.20))
    executive = clamp(100 - (risky_exec / max(1, len([d for d in dashboards if _is_executive(d)]))) * 80)
    overall = clamp(governance * 0.25 + trust * 0.25 + freshness * 0.20 + ownership * 0.15 + executive * 0.15)
    return HealthScores(overall, governance, trust, freshness, ownership, executive)


def _is_executive(dashboard: Dashboard) -> bool:
    return dashboard.business_domain == "Executive Reporting" or "executive" in dashboard.audience.lower() or dashboard.business_criticality == "critical"
