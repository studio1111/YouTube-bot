import json
from yt_agent.notifications import build_alert


def test_build_alert_from_warnings(tmp_path):
    experiment = tmp_path / "experiment.json"
    experiment.write_text(json.dumps({
        "experiment_id": "sky-001",
        "analytics": {
            "warnings": ["Missing Analytics rows for variants: B."],
            "result": {"status": "insufficient_data"},
        },
    }))
    alert = build_alert(str(experiment))
    assert "sky-001" in alert.subject
    assert "Missing Analytics" in alert.body


def test_build_alert_requires_warnings(tmp_path):
    experiment = tmp_path / "experiment.json"
    experiment.write_text(json.dumps({"analytics": {"warnings": []}}))
    try:
        build_alert(str(experiment))
    except ValueError as exc:
        assert "No Analytics warnings" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
