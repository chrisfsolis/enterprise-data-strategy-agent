"""Inventory metadata-quality linting utilities."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal

from enterprise_data_strategy_agent.config import HIGH_SENSITIVITY, STALE_DAYS_BY_CADENCE
from enterprise_data_strategy_agent.models import Inventory

Severity = Literal["error", "warning", "info"]
AssetType = Literal["dataset", "dashboard", "inventory"]

VALID_SENSITIVITY_LEVELS = {"public", "internal", *HIGH_SENSITIVITY}
VALID_USAGE_LEVELS = {"low", "medium", "high"}
VALID_CRITICALITY_LEVELS = {"low", "medium", "high", "critical"}
VALID_REFRESH_CADENCES = set(STALE_DAYS_BY_CADENCE)
VALID_DASHBOARD_TYPES = {"dashboard", "card"}


@dataclass(frozen=True)
class LintFinding:
    """Structured metadata-quality issue detected outside strategic analysis."""

    severity: Severity
    asset_type: AssetType
    asset_id: str
    message: str
    recommended_action: str


def lint_inventory(inventory: Inventory) -> list[LintFinding]:
    """Return metadata-quality findings for an already parsed inventory."""

    findings: list[LintFinding] = []
    dataset_counts = _counts(dataset.id for dataset in inventory.datasets)
    dashboard_counts = _counts(dashboard.id for dashboard in inventory.dashboards)

    for dataset_id, count in dataset_counts.items():
        if count > 1:
            findings.append(
                LintFinding(
                    "error",
                    "dataset",
                    dataset_id,
                    f"Dataset ID appears {count} times.",
                    "Assign a unique stable dataset ID to each dataset before analysis.",
                )
            )

    for dashboard_id, count in dashboard_counts.items():
        if count > 1:
            findings.append(
                LintFinding(
                    "error",
                    "dashboard",
                    dashboard_id,
                    f"Dashboard ID appears {count} times.",
                    "Assign a unique stable dashboard or card ID to each reporting asset.",
                )
            )

    downstream_dataset_ids = {dataset_id for dashboard in inventory.dashboards for dataset_id in dashboard.dataset_ids}
    dataset_by_id = {dataset.id: dataset for dataset in inventory.datasets}

    for dataset in inventory.datasets:
        _check_allowed(findings, "dataset", dataset.id, "sensitivity", dataset.sensitivity_level, VALID_SENSITIVITY_LEVELS)
        _check_allowed(findings, "dataset", dataset.id, "usage", dataset.usage_level, VALID_USAGE_LEVELS)
        _check_allowed(findings, "dataset", dataset.id, "criticality", dataset.business_criticality, VALID_CRITICALITY_LEVELS)
        _check_allowed(findings, "dataset", dataset.id, "refresh cadence", dataset.refresh_cadence, VALID_REFRESH_CADENCES)

        if dataset.row_count is None:
            findings.append(LintFinding("warning", "dataset", dataset.id, "Dataset row count is missing.", "Populate row_count so sizing, usage, and archival decisions have context."))
        elif dataset.row_count < 0:
            findings.append(LintFinding("error", "dataset", dataset.id, f"Dataset row count is negative ({dataset.row_count}).", "Correct row_count to a non-negative integer from source metadata."))

        if dataset.id not in downstream_dataset_ids:
            findings.append(LintFinding("info", "dataset", dataset.id, "Dataset has no downstream dashboards.", "Confirm whether this dataset should be archived, promoted, or connected to reporting assets."))

        if dataset.last_refreshed > inventory.generated_at:
            findings.append(LintFinding("error", "dataset", dataset.id, "Dataset last_refreshed is after the inventory generated_at date.", "Correct the refresh timestamp or regenerate the inventory with a later generated_at date."))

        if dataset.sensitivity_level in HIGH_SENSITIVITY and not dataset.steward:
            findings.append(LintFinding("warning", "dataset", dataset.id, "Sensitive dataset has no named steward.", "Assign a data steward responsible for access, definitions, and quality expectations."))

    for dashboard in inventory.dashboards:
        _check_allowed(findings, "dashboard", dashboard.id, "usage", dashboard.usage_level, VALID_USAGE_LEVELS)
        _check_allowed(findings, "dashboard", dashboard.id, "criticality", dashboard.business_criticality, VALID_CRITICALITY_LEVELS)
        _check_allowed(findings, "dashboard", dashboard.id, "dashboard type", dashboard.type, VALID_DASHBOARD_TYPES)

        if not dashboard.dataset_ids:
            findings.append(LintFinding("warning", "dashboard", dashboard.id, "Dashboard has no dataset_ids.", "Attach at least one upstream dataset or remove the orphaned dashboard metadata."))

        missing_dataset_ids = [dataset_id for dataset_id in dashboard.dataset_ids if dataset_id not in dataset_by_id]
        if missing_dataset_ids:
            findings.append(
                LintFinding(
                    "error",
                    "dashboard",
                    dashboard.id,
                    f"Dashboard references missing datasets: {', '.join(missing_dataset_ids)}.",
                    "Add the referenced datasets to inventory.datasets or remove stale dashboard dataset_ids.",
                )
            )

        uncertified = [dataset_by_id[dataset_id].id for dataset_id in dashboard.dataset_ids if dataset_id in dataset_by_id and not dataset_by_id[dataset_id].certified]
        if dashboard.certified and uncertified:
            findings.append(LintFinding("warning", "dashboard", dashboard.id, f"Certified dashboard is backed by uncertified datasets: {', '.join(uncertified)}.", "Certify upstream datasets or remove dashboard certification until dependencies are trusted."))

    return findings


def _counts(values: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts


def _check_allowed(findings: list[LintFinding], asset_type: AssetType, asset_id: str, label: str, value: str, allowed: set[str]) -> None:
    if value not in allowed:
        findings.append(
            LintFinding(
                "warning",
                asset_type,
                asset_id,
                f"Invalid {label} value '{value}'.",
                f"Use one of: {', '.join(sorted(allowed))}.",
            )
        )
