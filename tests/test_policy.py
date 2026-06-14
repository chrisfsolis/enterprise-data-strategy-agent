from dataclasses import replace
from datetime import timedelta

from enterprise_data_strategy_agent.linting import lint_inventory, generate_markdown_lint_report
from enterprise_data_strategy_agent.policy import DEFAULT_POLICY, StrategyPolicy, FreshnessThresholds, load_policy
from enterprise_data_strategy_agent.report import generate_markdown_report
from enterprise_data_strategy_agent.sample_loader import load_sample_inventory
from enterprise_data_strategy_agent.scoring import calculate_scores, is_stale
from enterprise_data_strategy_agent.analyzer import analyze_inventory
from enterprise_data_strategy_agent.cli import main


def test_policy_loads_from_sample_config():
    policy = load_policy("config/sample_strategy_policy.yml")

    assert policy.organization.name == "Acme Enterprise"
    assert policy.freshness_thresholds.daily_dataset_stale_after_days == 2
    assert policy.severity_overrides["stale_dataset"] == "high"


def test_missing_policy_values_fall_back_to_defaults(tmp_path):
    partial = tmp_path / "policy.yml"
    partial.write_text("organization:\n  name: Partial Co\n", encoding="utf-8")

    policy = load_policy(partial)

    assert policy.organization.name == "Partial Co"
    assert policy.organization.industry == DEFAULT_POLICY.organization.industry
    assert policy.freshness_thresholds.weekly_dataset_stale_after_days == DEFAULT_POLICY.freshness_thresholds.weekly_dataset_stale_after_days


def test_analyze_and_lint_work_with_config(tmp_path):
    brief = tmp_path / "brief.md"
    lint = tmp_path / "lint.md"

    assert main(["analyze", "--input", "data/sample_domo_inventory.json", "--output", str(brief), "--config", "config/sample_strategy_policy.yml"]) == 0
    assert main(["lint", "--input", "data/sample_domo_inventory.json", "--output", str(lint), "--config", "config/sample_strategy_policy.yml"]) == 0
    assert "## Strategy Policy Context" in brief.read_text(encoding="utf-8")
    assert "## Policy Context" in lint.read_text(encoding="utf-8")


def test_scoring_weights_still_produce_values_between_zero_and_100():
    inventory = load_sample_inventory("data/sample_domo_inventory.json")
    policy = load_policy("config/sample_strategy_policy.yml")
    scores = calculate_scores(inventory, policy)

    for value in scores.__dict__.values():
        assert 0 <= value <= 100


def test_stale_dataset_detection_respects_configured_thresholds():
    inventory = load_sample_inventory("data/sample_domo_inventory.json")
    dataset = next(dataset for dataset in inventory.datasets if dataset.refresh_cadence == "daily")
    dataset = replace(dataset, last_refreshed=inventory.generated_at - timedelta(days=3))
    lenient = StrategyPolicy(freshness_thresholds=FreshnessThresholds(daily_dataset_stale_after_days=5))
    strict = StrategyPolicy(freshness_thresholds=FreshnessThresholds(daily_dataset_stale_after_days=2))

    assert not is_stale(dataset, inventory.generated_at, lenient)
    assert is_stale(dataset, inventory.generated_at, strict)


def test_severity_override_changes_lint_finding_severity():
    inventory = load_sample_inventory("data/sample_domo_inventory.json")
    default = next(f for f in lint_inventory(inventory, DEFAULT_POLICY) if f.rule_id == "LINT006")
    policy = load_policy("config/sample_strategy_policy.yml")
    configured = next(f for f in lint_inventory(inventory, policy) if f.rule_id == "LINT006")

    assert default.severity != configured.severity
    assert configured.severity == "high"


def test_reports_include_policy_context():
    inventory = load_sample_inventory("data/sample_domo_inventory.json")
    policy = load_policy("config/sample_strategy_policy.yml")
    analysis = analyze_inventory(inventory, policy)

    assert "## Strategy Policy Context" in generate_markdown_report(inventory, analysis, policy)
    assert "Acme Enterprise" in generate_markdown_lint_report(inventory, analysis.lint_findings, policy)
