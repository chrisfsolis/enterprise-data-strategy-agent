"""Compatibility exports for metadata linting.

Structural payload validation lives in ``models.validate_inventory_payload``. Business
metadata linting lives in ``enterprise_data_strategy_agent.linting``.
"""

from enterprise_data_strategy_agent.linting import LintFinding, lint_inventory

__all__ = ["LintFinding", "lint_inventory"]
