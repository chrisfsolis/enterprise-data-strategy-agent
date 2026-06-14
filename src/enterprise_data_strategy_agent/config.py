"""Shared configuration constants for the strategy analyzer."""

STALE_DAYS_BY_CADENCE = {
    "hourly": 2,
    "daily": 3,
    "weekly": 14,
    "monthly": 45,
    "manual": 30,
}
DEFAULT_STALE_DAYS = 14

EXECUTIVE_DOMAINS = {"Executive Reporting", "Finance"}
EXECUTIVE_AUDIENCE_KEYWORDS = {"executive"}
CRITICALITY_LEVELS = {"critical"}
HIGH_SENSITIVITY = {"confidential", "restricted"}

CERTIFICATION_REQUIRED_DOMAINS = {"Executive Reporting", "Finance"}
CERTIFICATION_EXPECTED_FOR_CRITICAL_ASSETS = True

GOVERNANCE_UNCERTIFIED_WEIGHT = 35
GOVERNANCE_SENSITIVE_WITHOUT_STEWARD_PENALTY = 8
GOVERNANCE_MANUAL_REFRESH_PENALTY = 4

OWNERSHIP_MISSING_OWNER_WEIGHT = 70
OWNERSHIP_SENSITIVE_WITHOUT_STEWARD_PENALTY = 6

FRESHNESS_STALE_WEIGHT = 75
FRESHNESS_MANUAL_REFRESH_PENALTY = 3

EXECUTIVE_REPORTING_RISK_WEIGHT = 80

TRUST_SCORE_WEIGHTS = {
    "governance": 0.45,
    "freshness": 0.35,
    "ownership": 0.20,
}
OVERALL_SCORE_WEIGHTS = {
    "governance": 0.25,
    "trust": 0.25,
    "freshness": 0.20,
    "ownership": 0.15,
    "executive_reporting_risk": 0.15,
}
