import json
from pathlib import Path

from enterprise_data_strategy_agent.analyzer import analyze_inventory
from enterprise_data_strategy_agent.connectors.domo_mock import DomoMockConnector
from enterprise_data_strategy_agent.planning import build_remediation_backlog, generate_json_backlog, generate_markdown_remediation_plan
from enterprise_data_strategy_agent.policy import load_policy


def _sample():
    inventory = DomoMockConnector().load_inventory(Path("data/sample_domo_inventory.json"))
    policy = load_policy("config/sample_strategy_policy.yml")
    return inventory, analyze_inventory(inventory, policy), policy


def test_remediation_backlog_contains_items_and_urgent_lint_items():
    inventory, analysis, policy = _sample()

    items = build_remediation_backlog(inventory, analysis, policy)

    assert items
    assert any(item.priority in {"P0", "P1"} for item in items if item.severity in {"critical", "high"})


def test_executive_reporting_risks_are_prioritized_higher():
    inventory, analysis, policy = _sample()

    items = build_remediation_backlog(inventory, analysis, policy)
    executive_items = [item for item in items if "Executive" in item.affected_domain or "executive" in item.title.lower()]

    assert executive_items
    assert min(item.priority for item in executive_items) in {"P0", "P1"}


def test_json_backlog_output_is_valid_json():
    inventory, analysis, policy = _sample()

    payload = json.loads(generate_json_backlog(inventory, analysis, policy))

    assert "generated_at" in payload
    assert "policy_context" in payload
    assert payload["remediation_items"]


def test_markdown_plan_contains_expected_sections():
    inventory, analysis, policy = _sample()

    markdown = generate_markdown_remediation_plan(inventory, analysis, policy)

    for section in ["## Executive Summary", "## Policy Context", "## Remediation Backlog Summary", "## Stakeholder Engagement Plan", "## Success Measures", "## Notes"]:
        assert section in markdown


def test_all_scoring_values_remain_between_zero_and_one_hundred():
    _inventory, analysis, _policy = _sample()

    for score in analysis.scores.__dict__.values():
        assert 0 <= score <= 100
