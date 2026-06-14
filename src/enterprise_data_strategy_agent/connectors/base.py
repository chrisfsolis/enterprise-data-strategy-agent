"""Connector contracts for enterprise metadata sources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from enterprise_data_strategy_agent.models import Inventory


class MetadataConnector(ABC):
    """Read-only connector interface for analytics and governance metadata."""

    @abstractmethod
    def load_inventory(self, input_path: Path) -> Inventory:
        """Load and validate an enterprise metadata inventory."""
