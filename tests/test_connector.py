from pathlib import Path

from enterprise_data_strategy_agent.connectors.domo_mock import DomoMockConnector
from enterprise_data_strategy_agent.sample_loader import load_sample_inventory


def test_connector_loads_domo_mock_inventory():
    inventory = DomoMockConnector().load_inventory(Path("data/sample_domo_inventory.json"))
    assert inventory.platform.startswith("Domo-style")
    assert len(inventory.datasets) == 10
    assert len(inventory.dashboards) == 10


def test_sample_inventory_loads_correctly():
    inventory = load_sample_inventory("data/sample_domo_inventory.json")
    assert inventory.datasets[0].calculated_metrics
