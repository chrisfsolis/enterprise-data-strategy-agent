"""Shared configuration constants for the strategy analyzer."""

STALE_DAYS_BY_CADENCE = {
    "hourly": 2,
    "daily": 3,
    "weekly": 14,
    "monthly": 45,
    "manual": 30,
}

EXECUTIVE_DOMAINS = {"Executive Reporting", "Finance"}
HIGH_SENSITIVITY = {"confidential", "restricted"}
