from enterprise_data_strategy_agent.sample_loader import load_sample_inventory
from enterprise_data_strategy_agent.scoring import calculate_scores, explain_scores


def test_scoring_returns_values_between_zero_and_100():
    scores = calculate_scores(load_sample_inventory("data/sample_domo_inventory.json"))
    for value in scores.__dict__.values():
        assert 0 <= value <= 100


def test_scoring_explanations_include_factors_and_rationale():
    inventory = load_sample_inventory("data/sample_domo_inventory.json")
    scores = calculate_scores(inventory)
    explanations = explain_scores(inventory)

    assert set(explanations) == set(scores.__dict__)
    for name, explanation in explanations.items():
        assert explanation.score_name == name
        assert explanation.final_score == getattr(scores, name)
        assert explanation.rationale
        assert explanation.penalties_or_bonuses
