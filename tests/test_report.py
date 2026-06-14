from enterprise_data_strategy_agent.analyzer import analyze_inventory
from enterprise_data_strategy_agent.report import generate_markdown_report
from enterprise_data_strategy_agent.sample_loader import load_sample_inventory


def test_report_contains_expected_sections_and_disclaimer():
    inventory = load_sample_inventory("data/sample_domo_inventory.json")
    report = generate_markdown_report(inventory, analyze_inventory(inventory))
    for section in [
        "# Enterprise Data Strategy Brief",
        "## Executive Summary",
        "## Platform Context",
        "## Health Scores",
        "## Top Findings",
        "## Governance Gaps",
        "## Data Quality and Trust Issues",
        "## Metadata Quality Lint Findings",
        "## Dashboard and Reporting Risk",
        "## Trusted Data Product Opportunities",
        "## Recommended 30/60/90 Day Plan",
        "## Domo-Oriented Recommendations",
        "## Future Platform Opportunities",
        "## Next Steps",
    ]:
        assert section in report
    assert "not affiliated with, endorsed by, or sponsored by Domo" in report
    assert "Why:" in report
    assert "penalty" in report or "bonus" in report
    assert "Strategic trust findings below are generated separately" in report
    assert "Recommended action:" in report

from enterprise_data_strategy_agent.linting import generate_markdown_lint_report, lint_inventory


def test_markdown_lint_report_contains_expected_sections():
    inventory = load_sample_inventory("data/sample_domo_inventory.json")
    report = generate_markdown_lint_report(inventory, lint_inventory(inventory))

    for section in [
        "# Enterprise Data Metadata Lint Report",
        "## Summary",
        "## Critical Findings",
        "## High Findings",
        "## Medium Findings",
        "## Low Findings",
        "## Recommended Fix Order",
        "## Notes",
    ]:
        assert section in report
    assert "Linting is advisory" in report


def test_analyze_report_includes_metadata_lint_summary():
    inventory = load_sample_inventory("data/sample_domo_inventory.json")
    report = generate_markdown_report(inventory, analyze_inventory(inventory))

    assert "## Metadata Lint Summary" in report
    assert "Total lint findings" in report
