"""Remediation backlog models and prioritization helpers."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from typing import Literal

Priority = Literal["P0", "P1", "P2", "P3"]
EstimatedEffort = Literal["small", "medium", "large"]
ExpectedImpact = Literal["low", "medium", "high"]
TimeHorizon = Literal["immediate", "30_days", "60_days", "90_days", "later"]


@dataclass(frozen=True)
class RemediationItem:
    """Actionable unit of remediation work for enterprise data managers."""

    id: str
    title: str
    description: str
    priority: Priority
    severity: str
    affected_domain: str
    affected_object_type: str
    affected_object_id: str
    affected_object_name: str
    recommended_owner_role: str
    supporting_stakeholders: list[str]
    estimated_effort: EstimatedEffort
    expected_impact: ExpectedImpact
    time_horizon: TimeHorizon
    source_rule_id: str
    source_finding_title: str
    recommended_action: str
    success_measure: str

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""

        return asdict(self)


def summarize_backlog(items: list[RemediationItem]) -> dict[str, dict[str, int] | int]:
    """Summarize remediation items by planning dimensions."""

    return {
        "total_items": len(items),
        "by_priority": _count(items, "priority", ["P0", "P1", "P2", "P3"]),
        "by_severity": _count(items, "severity", ["critical", "high", "medium", "low"]),
        "by_effort": _count(items, "estimated_effort", ["small", "medium", "large"]),
        "by_time_horizon": _count(items, "time_horizon", ["immediate", "30_days", "60_days", "90_days", "later"]),
    }


def _count(items: list[RemediationItem], attribute: str, order: list[str]) -> dict[str, int]:
    counts = Counter(str(getattr(item, attribute)) for item in items)
    return {key: counts.get(key, 0) for key in order}
