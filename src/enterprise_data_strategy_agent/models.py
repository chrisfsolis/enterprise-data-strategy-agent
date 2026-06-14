"""Typed domain models and validation helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any


@dataclass(frozen=True)
class CalculatedMetric:
    """A Beast Mode-style calculated metric definition."""

    name: str
    expression: str
    dataset_id: str
    business_definition: str = ""


@dataclass(frozen=True)
class Dataset:
    """Dataset metadata used by the analyzer."""

    id: str
    name: str
    business_domain: str
    owner: str | None
    department: str
    refresh_cadence: str
    last_refreshed: date
    certified: bool
    row_count: int | None
    sensitivity_level: str
    usage_level: str
    business_criticality: str
    steward: str | None = None
    data_quality_notes: str = ""
    calculated_metrics: list[CalculatedMetric] = field(default_factory=list)


@dataclass(frozen=True)
class Dashboard:
    """Dashboard or card metadata."""

    id: str
    title: str
    type: str
    business_domain: str
    owner: str | None
    department: str
    certified: bool
    usage_level: str
    business_criticality: str
    dataset_ids: list[str]
    audience: str
    last_viewed: date | None = None


@dataclass(frozen=True)
class Inventory:
    """Validated enterprise analytics inventory."""

    platform: str
    generated_at: date
    datasets: list[Dataset]
    dashboards: list[Dashboard]


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


def validate_inventory_payload(payload: dict[str, Any]) -> Inventory:
    """Validate and convert a raw inventory JSON payload into typed models."""

    required = {"platform", "generated_at", "datasets", "dashboards"}
    missing = required.difference(payload)
    if missing:
        raise ValueError(f"Inventory is missing required keys: {sorted(missing)}")
    if not isinstance(payload["datasets"], list) or not isinstance(payload["dashboards"], list):
        raise ValueError("Inventory datasets and dashboards must be lists")

    datasets: list[Dataset] = []
    for raw in payload["datasets"]:
        metrics = [CalculatedMetric(**metric) for metric in raw.get("calculated_metrics", [])]
        datasets.append(
            Dataset(
                id=raw["id"],
                name=raw["name"],
                business_domain=raw["business_domain"],
                owner=raw.get("owner"),
                department=raw["department"],
                refresh_cadence=raw["refresh_cadence"].lower(),
                last_refreshed=_parse_date(raw["last_refreshed"]),  # type: ignore[arg-type]
                certified=bool(raw["certified"]),
                row_count=int(raw["row_count"]) if raw.get("row_count") is not None else None,
                sensitivity_level=raw["sensitivity_level"].lower(),
                usage_level=raw["usage_level"].lower(),
                business_criticality=raw["business_criticality"].lower(),
                steward=raw.get("steward"),
                data_quality_notes=raw.get("data_quality_notes", ""),
                calculated_metrics=metrics,
            )
        )

    dataset_ids = {dataset.id for dataset in datasets}
    dashboards: list[Dashboard] = []
    for raw in payload["dashboards"]:
        unknown = set(raw["dataset_ids"]).difference(dataset_ids)
        if unknown:
            raise ValueError(f"Dashboard {raw['id']} references unknown datasets: {sorted(unknown)}")
        dashboards.append(
            Dashboard(
                id=raw["id"],
                title=raw["title"],
                type=raw["type"],
                business_domain=raw["business_domain"],
                owner=raw.get("owner"),
                department=raw["department"],
                certified=bool(raw["certified"]),
                usage_level=raw["usage_level"].lower(),
                business_criticality=raw["business_criticality"].lower(),
                dataset_ids=list(raw["dataset_ids"]),
                audience=raw["audience"],
                last_viewed=_parse_date(raw.get("last_viewed")),
            )
        )

    return Inventory(
        platform=payload["platform"],
        generated_at=_parse_date(payload["generated_at"]),  # type: ignore[arg-type]
        datasets=datasets,
        dashboards=dashboards,
    )
