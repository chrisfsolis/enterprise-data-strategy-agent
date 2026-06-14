"""Business metadata linting for enterprise analytics inventories."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Literal

from enterprise_data_strategy_agent.config import HIGH_SENSITIVITY
from enterprise_data_strategy_agent.policy import DEFAULT_POLICY, StrategyPolicy
from enterprise_data_strategy_agent.models import Inventory
from enterprise_data_strategy_agent.scoring import is_stale

Severity = Literal["critical", "high", "medium", "low"]


@dataclass(frozen=True)
class LintFinding:
    """A user-facing metadata governance finding."""

    rule_id: str
    severity: Severity
    title: str
    description: str
    affected_object_type: str
    affected_object_id: str
    affected_object_name: str
    recommendation: str

    @property
    def asset_type(self) -> str:
        """Backward-compatible alias for older report code/tests."""
        return self.affected_object_type

    @property
    def asset_id(self) -> str:
        """Backward-compatible alias for older report code/tests."""
        return self.affected_object_id

    @property
    def message(self) -> str:
        """Backward-compatible concise finding text."""
        return self.description

    @property
    def recommended_action(self) -> str:
        """Backward-compatible alias for recommendation."""
        return self.recommendation


def lint_inventory(inventory: Inventory, policy: StrategyPolicy | None = None) -> list[LintFinding]:
    """Return advisory business metadata lint findings for a parsed inventory."""

    active_policy = policy or DEFAULT_POLICY
    findings: list[LintFinding] = []
    for dataset_id, count in Counter(dataset.id for dataset in inventory.datasets).items():
        if count > 1:
            findings.append(_finding("LINT013", "critical", "Duplicate dataset ID", f"Dataset ID appears {count} times.", "dataset", dataset_id, dataset_id, "Assign a unique stable dataset ID to each dataset before analysis."))
    for dashboard_id, count in Counter(dashboard.id for dashboard in inventory.dashboards).items():
        if count > 1:
            findings.append(_finding("LINT014", "critical", "Duplicate dashboard/card ID", f"Dashboard ID appears {count} times.", "dashboard", dashboard_id, dashboard_id, "Assign a unique stable dashboard or card ID to each reporting asset."))

    dataset_by_id = {dataset.id: dataset for dataset in inventory.datasets}
    downstream_ids = {dataset_id for dashboard in inventory.dashboards for dataset_id in dashboard.dataset_ids}

    for dashboard in inventory.dashboards:
        _check_allowed(findings, "dashboard", dashboard.id, dashboard.title, "usage", dashboard.usage_level, {"low", "medium", "high"})
        _check_allowed(findings, "dashboard", dashboard.id, dashboard.title, "criticality", dashboard.business_criticality, {"low", "medium", "high", "critical"})
        _check_allowed(findings, "dashboard", dashboard.id, dashboard.title, "dashboard type", dashboard.type, {"dashboard", "card"})
        linked = [dataset_by_id[dataset_id] for dataset_id in dashboard.dataset_ids if dataset_id in dataset_by_id]
        missing_ids = [dataset_id for dataset_id in dashboard.dataset_ids if dataset_id not in dataset_by_id]

        if missing_ids:
            findings.append(_finding("LINT001", active_policy.severity("missing_dataset_reference", "critical"), "Dashboard or card references missing datasets", f"Dashboard references missing datasets: {', '.join(missing_ids)}.", "dashboard", dashboard.id, dashboard.title, "Add the referenced datasets to inventory.datasets or remove stale dashboard/card dataset_ids."))
        if not dashboard.owner:
            findings.append(_finding("LINT003", active_policy.severity("missing_dashboard_owner", "high" if dashboard.business_criticality == "critical" else "medium"), "Dashboard or card owner is missing", "Dashboard/card has no accountable business owner.", "dashboard", dashboard.id, dashboard.title, "Assign a business owner who can approve definitions, certification, and remediation decisions."))
        if not dashboard.dataset_ids:
            findings.append(_finding("LINT011", active_policy.severity("dashboard_without_datasets", "medium"), "Dashboard has no linked datasets", "Dashboard has no dataset_ids / no linked datasets.", "dashboard", dashboard.id, dashboard.title, "Attach upstream datasets or archive/remove the orphaned dashboard metadata."))

        uncertified = [dataset.name for dataset in linked if not dataset.certified]
        executive = "executive" in dashboard.audience.lower() or "executive" in dashboard.business_domain.lower()
        if executive and uncertified:
            findings.append(_finding("LINT004", active_policy.severity("executive_dashboard_uncertified_source", "high"), "Executive dashboard uses uncertified datasets", f"Executive dashboard is powered by uncertified datasets: {', '.join(uncertified)}.", "dashboard", dashboard.id, dashboard.title, "Certify upstream datasets or clearly label the dashboard as not certified for executive decision-making."))
        if dashboard.certified and uncertified:
            findings.append(_finding("LINT010", "high", "Certified dashboard uses uncertified datasets", f"Certified dashboard is backed by uncertified datasets: {', '.join(uncertified)}.", "dashboard", dashboard.id, dashboard.title, "Certify upstream datasets or remove dashboard certification until dependencies are trusted."))

        manual = [dataset.name for dataset in linked if dataset.refresh_cadence == "manual"]
        if dashboard.business_criticality == "critical" and manual:
            findings.append(_finding("LINT007", active_policy.severity("manual_refresh_high_criticality", "high"), "Critical dashboard depends on manually refreshed data", f"High-criticality dashboard uses manually refreshed datasets: {', '.join(manual)}.", "dashboard", dashboard.id, dashboard.title, "Move these datasets to scheduled refreshes with freshness alerts and documented SLAs."))

    for dataset in inventory.datasets:
        _check_allowed(findings, "dataset", dataset.id, dataset.name, "sensitivity", dataset.sensitivity_level, {"public", "internal", *HIGH_SENSITIVITY})
        _check_allowed(findings, "dataset", dataset.id, dataset.name, "usage", dataset.usage_level, {"low", "medium", "high"})
        _check_allowed(findings, "dataset", dataset.id, dataset.name, "criticality", dataset.business_criticality, {"low", "medium", "high", "critical"})
        _check_allowed(findings, "dataset", dataset.id, dataset.name, "refresh cadence", dataset.refresh_cadence, active_policy.freshness_thresholds.cadences())
        if dataset.row_count is None:
            findings.append(_finding("LINT015", "low", "Dataset row count is missing", "Dataset row count is missing.", "dataset", dataset.id, dataset.name, "Populate row_count so sizing, usage, and archival decisions have context."))
        elif dataset.row_count < 0:
            findings.append(_finding("LINT016", "high", "Dataset row count is negative", f"Dataset row count is negative ({dataset.row_count}).", "dataset", dataset.id, dataset.name, "Correct row_count to a non-negative integer from source metadata."))
        if dataset.last_refreshed > inventory.generated_at:
            findings.append(_finding("LINT017", "high", "Dataset refresh date is in the future", "Dataset last_refreshed is after the inventory generated_at date.", "dataset", dataset.id, dataset.name, "Correct the refresh timestamp or regenerate the inventory with a later generated_at date."))
        if not dataset.owner:
            findings.append(_finding("LINT002", active_policy.severity("missing_dataset_owner", "high" if dataset.business_criticality == "critical" else "medium"), "Dataset owner is missing", "Dataset has no accountable business owner.", "dataset", dataset.id, dataset.name, "Assign a business owner responsible for definitions, quality expectations, and escalation."))
        if dataset.sensitivity_level in HIGH_SENSITIVITY and not (dataset.owner or dataset.steward):
            findings.append(_finding("LINT005", active_policy.severity("sensitive_dataset_without_owner", "critical"), "Sensitive dataset lacks stewardship", "Sensitive dataset has no steward or owner.", "dataset", dataset.id, dataset.name, "Assign both an owner and a steward before broadening access or certification."))
        elif dataset.sensitivity_level in HIGH_SENSITIVITY and not dataset.steward:
            findings.append(_finding("LINT005", active_policy.severity("sensitive_dataset_without_owner", "high"), "Sensitive dataset lacks stewardship", "Sensitive dataset has no named steward.", "dataset", dataset.id, dataset.name, "Assign a data steward responsible for access, definitions, and quality expectations."))
        if is_stale(dataset, inventory.generated_at, active_policy):
            findings.append(_finding("LINT006", active_policy.severity("stale_dataset", "high" if dataset.business_criticality == "critical" else "medium"), "Dataset is stale", f"Dataset last refreshed on {dataset.last_refreshed.isoformat()} is stale for its {dataset.refresh_cadence} cadence.", "dataset", dataset.id, dataset.name, "Refresh the dataset, correct the cadence metadata, or document why stale data is acceptable."))
        if dataset.row_count and dataset.row_count >= active_policy.usage_thresholds.high_row_count_threshold and dataset.usage_level == "low":
            findings.append(_finding("LINT009", "low", "High-row-count dataset has low usage", f"Dataset has {dataset.row_count:,} rows but low usage.", "dataset", dataset.id, dataset.name, "Review whether this dataset should be archived, summarized, promoted, or redesigned as a governed data product."))
        if dataset.id not in downstream_ids:
            findings.append(_finding("LINT012", active_policy.severity("orphan_dataset", "low"), "Dataset has no downstream dashboards or cards", "Dataset has no downstream dashboards/cards.", "dataset", dataset.id, dataset.name, "Confirm whether this dataset should be archived, promoted, or connected to reporting assets."))

    _add_duplicate_metric_findings(inventory, findings, active_policy)
    return sorted(findings, key=lambda f: ({"critical": 0, "high": 1, "medium": 2, "low": 3}[f.severity], f.rule_id, f.affected_object_id))


def _add_duplicate_metric_findings(inventory: Inventory, findings: list[LintFinding], policy: StrategyPolicy) -> None:
    by_normalized: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for dataset in inventory.datasets:
        for metric in dataset.calculated_metrics:
            normalized = metric.name.strip().lower().replace("_", " ").replace("-", " ")
            by_normalized[normalized].append((dataset.name, metric.name))
    for normalized, occurrences in by_normalized.items():
        display_names = sorted({name for _, name in occurrences})
        if len(occurrences) > 1 or len(display_names) > 1:
            findings.append(_finding("LINT008", policy.severity("duplicate_metric", "medium"), "Duplicate or inconsistent calculated metric names", f"Calculated metric name '{normalized}' appears multiple times or with inconsistent formatting: {', '.join(display_names)}.", "metric", normalized, normalized, "Standardize metric naming, definitions, owners, and approved calculation logic."))


def _finding(rule_id: str, severity: Severity, title: str, description: str, object_type: str, object_id: str, object_name: str, recommendation: str) -> LintFinding:
    return LintFinding(rule_id, severity, title, description, object_type, object_id, object_name, recommendation)


def generate_markdown_lint_report(inventory: Inventory, findings: list[LintFinding], policy: StrategyPolicy | None = None) -> str:
    """Generate a markdown metadata lint report."""

    active_policy = policy or DEFAULT_POLICY
    counts = {severity: sum(1 for f in findings if f.severity == severity) for severity in ("critical", "high", "medium", "low")}
    lines = [
        "# Enterprise Data Metadata Lint Report",
        "",
        "## Summary",
        f"Inventory generated at: {inventory.generated_at.isoformat()}",
        f"Datasets: {len(inventory.datasets)}",
        f"Dashboards/cards: {len(inventory.dashboards)}",
        f"Total findings: {len(findings)}",
        *[f"- {severity.title()}: {counts[severity]}" for severity in ("critical", "high", "medium", "low")],
        "",
        "## Policy Context",
        f"Policy settings: {active_policy.source_path if active_policy.source_path else 'Default policy settings'}",
        f"Organization: {active_policy.organization.name}",
        "",
    ]
    for severity in ("critical", "high", "medium", "low"):
        lines.append(f"## {severity.title()} Findings")
        severity_findings = [f for f in findings if f.severity == severity]
        if not severity_findings:
            lines.append("- No findings.")
        for finding in severity_findings:
            lines.extend([f"- **{finding.rule_id}: {finding.title}**", f"  - Affected: {finding.affected_object_type} `{finding.affected_object_id}` ({finding.affected_object_name})", f"  - Detail: {finding.description}", f"  - Recommendation: {finding.recommendation}"])
        lines.append("")
    lines.extend([
        "## Recommended Fix Order",
        "Fix critical findings first because missing upstream data and sensitive-data stewardship gaps can undermine trust, access control, and executive reporting. Next address high-severity certification, ownership, stale-data, and manual-refresh issues that affect decision-critical dashboards. Then resolve medium and low findings to improve maintainability, reduce clutter, and strengthen long-term governance.",
        "",
        "## Notes",
        "Linting is advisory: it reports metadata quality and governance issues, does not modify the source platform, and should not block structural parsing unless the inventory payload itself is malformed.",
    ])
    return "\n".join(lines)


def _check_allowed(findings: list[LintFinding], object_type: str, object_id: str, object_name: str, label: str, value: str, allowed: set[str]) -> None:
    if value not in allowed:
        findings.append(_finding("LINT018", "medium", f"Invalid {label} value", f"Invalid {label} value '{value}'.", object_type, object_id, object_name, f"Use one of: {', '.join(sorted(allowed))}."))
