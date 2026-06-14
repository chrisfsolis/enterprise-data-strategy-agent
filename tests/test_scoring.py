from enterprise_data_strategy_agent.sample_loader import load_sample_inventory
from enterprise_data_strategy_agent.scoring import calculate_scores


def test_scoring_returns_values_between_zero_and_100():
    scores = calculate_scores(load_sample_inventory("data/sample_domo_inventory.json"))
    for value in scores.__dict__.values():
        assert 0 <= value <= 100
