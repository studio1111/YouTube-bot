import json
from yt_agent.analytics import VariantMetrics, calculate_winner, snapshot_experiment


def test_requires_minimum_sample():
    result = calculate_winner([VariantMetrics("A", 99, 10, 0.2), VariantMetrics("B", 100, 11, 0.1)])
    assert result.status == "insufficient_data"
    assert result.winner is None


def test_picks_highest_ctr():
    result = calculate_winner([VariantMetrics("A", 120, 10, 0.12), VariantMetrics("B", 130, 12, 0.09)])
    assert result.status == "winner_found"
    assert result.winner == "A"


def test_snapshot(tmp_path):
    experiment = tmp_path / "experiment.json"
    experiment.write_text(json.dumps({"variants": [{"id": "A"}, {"id": "B"}]}))
    output = snapshot_experiment(str(experiment), [VariantMetrics("A", 100, 15, 0.15), VariantMetrics("B", 100, 12, 0.12)])
    data = json.loads(output.read_text())
    assert data["analytics"]["result"]["winner"] == "A"
