import json
from pathlib import Path

from yt_agent.analytics import _extract_rows, calculate_winner


FIXTURE = Path(__file__).parent / "fixtures" / "youtube_analytics_variant_sample.json"


def test_sample_api_payload_produces_a_real_winner():
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    metrics = _extract_rows(payload, ["A", "B"])
    result = calculate_winner(metrics, min_impressions=100)

    assert [(item.variant_id, item.impressions, item.views) for item in metrics] == [
        ("A", 1250, 138),
        ("B", 1190, 112),
    ]
    assert result.status == "winner_found"
    assert result.winner == "A"
    assert "Highest CTR" in result.reason


def test_unknown_variants_are_ignored():
    payload = {"rows": [["A", "100", "10", "0.10"], ["CONTROL", "999", "99", "0.99"]]}
    metrics = _extract_rows(payload, ["A", "B"])
    assert [item.variant_id for item in metrics] == ["A"]
