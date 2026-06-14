"""Compatibility tests for metadata linting behavior."""

from pathlib import Path

from enterprise_data_strategy_agent.connectors.domo_mock import DomoMockConnector
from enterprise_data_strategy_agent.linting import lint_inventory


def test_linting_finds_advisory_governance_issues():
    inventory = DomoMockConnector().load_inventory(Path("data/sample_domo_inventory.json"))
    findings = lint_inventory(inventory)

    assert findings
    assert {finding.severity for finding in findings} <= {"critical", "high", "medium", "low"}
