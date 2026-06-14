"""Configurable strategy policy for enterprise data strategy analysis."""

from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class OrganizationPolicy:
    name: str = "Sample Enterprise"
    industry: str = "Cross-industry"
    data_maturity_stage: str = "Developing governed analytics"
    primary_platform: str = "Domo-style BI metadata"
    strategy_owner_role: str = "Enterprise Data Manager"

@dataclass(frozen=True)
class FreshnessThresholds:
    daily_dataset_stale_after_days: int = 3
    weekly_dataset_stale_after_days: int = 14
    monthly_dataset_stale_after_days: int = 45
    manual_dataset_review_after_days: int = 30
    hourly_dataset_stale_after_days: int = 2
    default_dataset_stale_after_days: int = 14

    def for_cadence(self, cadence: str) -> int:
        return {
            "hourly": self.hourly_dataset_stale_after_days,
            "daily": self.daily_dataset_stale_after_days,
            "weekly": self.weekly_dataset_stale_after_days,
            "monthly": self.monthly_dataset_stale_after_days,
            "manual": self.manual_dataset_review_after_days,
        }.get(cadence, self.default_dataset_stale_after_days)

    def cadences(self) -> set[str]:
        return {"hourly", "daily", "weekly", "monthly", "manual"}

@dataclass(frozen=True)
class UsageThresholds:
    high_row_count_threshold: int = 1_000_000
    low_usage_threshold: int = 10
    high_usage_threshold: int = 100

@dataclass(frozen=True)
class RiskThresholds:
    executive_dashboard_minimum_certification_required: bool = True
    sensitive_data_requires_owner: bool = True
    sensitive_data_requires_steward: bool = True
    high_criticality_requires_certified_sources: bool = True

@dataclass(frozen=True)
class ScoringWeights:
    governance: float = 0.25
    trust: float = 0.25
    freshness: float = 0.20
    ownership: float = 0.15
    executive_reporting_risk: float = 0.15

    def normalized(self) -> dict[str, float]:
        values = {field.name: float(getattr(self, field.name)) for field in fields(self)}
        total = sum(value for value in values.values() if value > 0)
        if total <= 0:
            return DEFAULT_POLICY.scoring_weights.normalized()
        return {name: max(0.0, value) / total for name, value in values.items()}


DEFAULT_SEVERITY_OVERRIDES = {
    "missing_dataset_reference": "critical",
    "missing_dataset_owner": "medium",
    "missing_dashboard_owner": "medium",
    "executive_dashboard_uncertified_source": "high",
    "sensitive_dataset_without_owner": "critical",
    "stale_dataset": "medium",
    "manual_refresh_high_criticality": "high",
    "duplicate_metric": "medium",
    "orphan_dataset": "low",
    "dashboard_without_datasets": "medium",
}

@dataclass(frozen=True)
class StrategyPolicy:
    organization: OrganizationPolicy = field(default_factory=OrganizationPolicy)
    freshness_thresholds: FreshnessThresholds = field(default_factory=FreshnessThresholds)
    usage_thresholds: UsageThresholds = field(default_factory=UsageThresholds)
    risk_thresholds: RiskThresholds = field(default_factory=RiskThresholds)
    scoring_weights: ScoringWeights = field(default_factory=ScoringWeights)
    severity_overrides: dict[str, str] = field(default_factory=lambda: dict(DEFAULT_SEVERITY_OVERRIDES))
    trusted_data_product_domains: list[str] = field(default_factory=lambda: ["Executive Reporting", "Finance", "Sales", "Customer Success", "Operations"])
    stakeholder_roles: list[str] = field(default_factory=lambda: ["Enterprise Data Manager", "Domo Admin", "Finance Leader", "Sales Operations Leader", "Customer Success Operations Leader", "Data Governance Owner", "Security or Compliance Partner"])
    source_path: str | None = None

    def severity(self, key: str, fallback: str) -> str:
        value = self.severity_overrides.get(key, fallback)
        return value if value in {"critical", "high", "medium", "low"} else fallback


DEFAULT_POLICY = StrategyPolicy()


def load_policy(config_path: str | Path | None = None) -> StrategyPolicy:
    """Load a strategy policy YAML file and merge it with defaults."""

    if config_path is None:
        return DEFAULT_POLICY
    path = Path(config_path)
    raw = _load_simple_yaml(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("strategy policy must be a YAML mapping")
    policy = _merge_policy(raw)
    return StrategyPolicy(**{**policy.__dict__, "source_path": str(path)})


def _merge_policy(raw: dict[str, Any]) -> StrategyPolicy:
    default = DEFAULT_POLICY
    allowed = {field.name for field in fields(StrategyPolicy)} - {"source_path"}
    unknown = set(raw) - allowed
    if unknown:
        raise ValueError(f"unknown strategy policy section(s): {', '.join(sorted(unknown))}")
    return StrategyPolicy(
        organization=_merge_dataclass(default.organization, raw.get("organization", {})),
        freshness_thresholds=_merge_dataclass(default.freshness_thresholds, raw.get("freshness_thresholds", {})),
        usage_thresholds=_merge_dataclass(default.usage_thresholds, raw.get("usage_thresholds", {})),
        risk_thresholds=_merge_dataclass(default.risk_thresholds, raw.get("risk_thresholds", {})),
        scoring_weights=_merge_dataclass(default.scoring_weights, raw.get("scoring_weights", {})),
        severity_overrides={**default.severity_overrides, **_expect_mapping(raw.get("severity_overrides", {}), "severity_overrides")},
        trusted_data_product_domains=list(raw.get("trusted_data_product_domains", default.trusted_data_product_domains)),
        stakeholder_roles=list(raw.get("stakeholder_roles", default.stakeholder_roles)),
    )


def _merge_dataclass(default: Any, raw: Any) -> Any:
    if not is_dataclass(default):
        raise TypeError("default must be a dataclass")
    data = _expect_mapping(raw, type(default).__name__)
    allowed = {field.name for field in fields(default)}
    unknown = set(data) - allowed
    if unknown:
        raise ValueError(f"unknown {type(default).__name__} setting(s): {', '.join(sorted(unknown))}")
    return type(default)(**{**default.__dict__, **data})


def _expect_mapping(raw: Any, label: str) -> dict[str, Any]:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError(f"{label} must be a mapping")
    return raw



def _load_simple_yaml(text: str) -> dict[str, Any]:
    """Parse the small YAML subset used by strategy policy files."""

    root: dict[str, Any] = {}
    current_section: str | None = None
    current_list: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        if indent == 0:
            if stripped.endswith(":"):
                current_section = stripped[:-1]
                current_list = None
                root[current_section] = {}
            else:
                key, value = _split_yaml_key_value(stripped)
                root[key] = _parse_scalar(value)
                current_section = None
                current_list = None
            continue
        if current_section is None:
            raise ValueError(f"invalid indented policy setting: {stripped}")
        if stripped.startswith("- "):
            if current_list is None:
                root[current_section] = []
                current_list = current_section
            if not isinstance(root[current_section], list):
                raise ValueError(f"mixed mapping/list values in {current_section}")
            root[current_section].append(_parse_scalar(stripped[2:].strip()))
            continue
        key, value = _split_yaml_key_value(stripped)
        if not isinstance(root[current_section], dict):
            raise ValueError(f"mixed list/mapping values in {current_section}")
        root[current_section][key] = _parse_scalar(value)
        current_list = None
    return root


def _split_yaml_key_value(line: str) -> tuple[str, str]:
    if ":" not in line:
        raise ValueError(f"invalid policy line: {line}")
    key, value = line.split(":", 1)
    return key.strip(), value.strip()


def _parse_scalar(value: str) -> Any:
    if value == "":
        return {}
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value.strip('"\'')
