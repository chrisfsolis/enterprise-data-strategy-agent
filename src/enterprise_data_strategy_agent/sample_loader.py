"""Convenience functions for loading sample inventories."""

from __future__ import annotations

from pathlib import Path

from enterprise_data_strategy_agent.connectors.domo_mock import DomoMockConnector
from enterprise_data_strategy_agent.models import Inventory


def load_sample_inventory(path: str | Path) -> Inventory:
    """Load a synthetic Domo-style inventory from a JSON file."""

    return DomoMockConnector().load_inventory(Path(path))
