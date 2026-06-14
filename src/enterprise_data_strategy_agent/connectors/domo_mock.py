"""Synthetic Domo-style connector used for demos and tests."""

from __future__ import annotations

import json
from pathlib import Path

from enterprise_data_strategy_agent.connectors.base import MetadataConnector
from enterprise_data_strategy_agent.models import Inventory, validate_inventory_payload


class DomoMockConnector(MetadataConnector):
    """Load Domo-style metadata from local JSON without calling Domo APIs."""

    def load_inventory(self, input_path: Path) -> Inventory:
        """Load a synthetic Domo-style inventory from disk."""

        with input_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        return validate_inventory_payload(payload)
