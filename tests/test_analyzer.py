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
