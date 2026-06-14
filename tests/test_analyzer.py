from enterprise_data_strategy_agent.analyzer import analyze_inventory
from enterprise_data_strategy_agent.sample_loader import load_sample_inventory


def test_analyzer_returns_findings():
    result = analyze_inventory(load_sample_inventory("data/sample_domo_inventory.json"))
    assert result.top_risks
    assert result.quick_wins
    assert result.risky_dashboards
    assert result.duplicate_metrics


def test_analyzer_exposes_score_explanations():
    result = analyze_inventory(load_sample_inventory("data/sample_domo_inventory.json"))
    assert result.score_explanations["overall"].final_score == result.scores.overall
    assert result.score_explanations["freshness"].rationale


def test_analyzer_handles_dashboard_missing_dataset_reference():
    inventory = load_sample_inventory("data/sample_domo_inventory.json")
    broken_dashboard = inventory.dashboards[0]
    broken_dashboard = type(broken_dashboard)(
        id="dash_missing_dataset",
        title="Missing Dataset Dashboard",
        type=broken_dashboard.type,
        business_domain=broken_dashboard.business_domain,
        owner=broken_dashboard.owner,
        department=broken_dashboard.department,
        certified=broken_dashboard.certified,
        usage_level=broken_dashboard.usage_level,
        business_criticality="critical",
        dataset_ids=["ds_missing_from_inventory"],
        audience="Executive Leadership",
        last_viewed=broken_dashboard.last_viewed,
    )
    inventory = type(inventory)(
        platform=inventory.platform,
        generated_at=inventory.generated_at,
        datasets=inventory.datasets,
        dashboards=[broken_dashboard],
    )

    result = analyze_inventory(inventory)

    assert any("references missing datasets: ds_missing_from_inventory" in dashboard for dashboard in result.risky_dashboards)
    assert any("Dashboard references missing datasets: ds_missing_from_inventory" in finding.message for finding in result.lint_findings)
