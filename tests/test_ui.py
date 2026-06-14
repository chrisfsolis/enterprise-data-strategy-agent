import json

import pytest

from enterprise_data_strategy_agent.analyzer import analyze_inventory
from enterprise_data_strategy_agent.sample_loader import load_sample_inventory
from enterprise_data_strategy_agent.ui import (
    build_report_bundle,
    format_score_rows,
    generate_report_artifacts,
    load_bundled_sample_inventory,
    load_bundled_sample_policy,
    parse_inventory_json,
    summarize_inventory,
)


def test_parse_inventory_json_accepts_bytes_and_validates_inventory():
    raw = open("data/sample_domo_inventory.json", "rb").read()

    inventory = parse_inventory_json(raw)

    assert inventory.platform == "Domo-style reference metadata"
    assert len(inventory.datasets) == 10
    assert len(inventory.dashboards) == 10


def test_parse_inventory_json_rejects_non_object_payload():
    with pytest.raises(ValueError, match="top level"):
        parse_inventory_json(json.dumps([{"platform": "not valid"}]))


def test_format_score_rows_returns_all_labeled_scores():
    inventory = load_sample_inventory("data/sample_domo_inventory.json")
    analysis = analyze_inventory(inventory)

    rows = format_score_rows(analysis)

    assert [row["Score"] for row in rows] == [
        "Overall",
        "Governance",
        "Trust",
        "Freshness",
        "Ownership",
        "Executive reporting risk",
    ]
    assert all(isinstance(row["Value"], int) for row in rows)
    assert all(row["Why"] for row in rows)


def test_summarize_inventory_counts_assets():
    inventory = load_sample_inventory("data/sample_domo_inventory.json")

    summary = summarize_inventory(inventory)

    assert summary["Platform"] == "Domo-style reference metadata"
    assert summary["Generated at"] == "2026-06-14"
    assert summary["Datasets"] == 10
    assert summary["Dashboards/cards"] == 10
    assert summary["Certified datasets"] == 5
    assert summary["Uncertified datasets"] == 5
    assert summary["Sensitive datasets"] >= 1
    assert summary["Executive dashboards/cards"] >= 1
    assert "Finance" in summary["Business domains"]


def test_build_report_bundle_returns_analysis_and_markdown():
    inventory = load_sample_inventory("data/sample_domo_inventory.json")

    analysis, report = build_report_bundle(inventory)

    assert analysis.top_risks
    assert report.startswith("# Enterprise Data Strategy Brief")


def test_ui_helper_loads_bundled_sample_inventory():
    inventory = load_bundled_sample_inventory()

    assert inventory.platform == "Domo-style reference metadata"
    assert len(inventory.datasets) == 10
    assert len(inventory.dashboards) == 10


def test_ui_helper_loads_bundled_sample_policy():
    policy = load_bundled_sample_policy()

    assert policy.organization.name
    assert policy.organization.primary_platform
    assert policy.source_path == "config/sample_strategy_policy.yml"


def test_ui_helper_generates_all_report_artifacts_from_sample_data():
    inventory = load_bundled_sample_inventory()
    policy = load_bundled_sample_policy()

    artifacts = generate_report_artifacts(inventory, policy)

    assert artifacts.strategy_brief_markdown.startswith("# Enterprise Data Strategy Brief")
    assert artifacts.lint_report_markdown.startswith("# Enterprise Data Metadata Lint Report")
    assert artifacts.remediation_plan_markdown.startswith("# Enterprise Data Remediation Plan")
    backlog = json.loads(artifacts.remediation_backlog_json)
    assert backlog["remediation_items"]
    assert set(backlog) >= {"generated_at", "policy_context", "summary", "remediation_items"}
