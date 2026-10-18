import json
from yt_agent.ab_test import create_experiment, title_variants


def test_has_two_variants():
    variants = title_variants("The ocean mystery")
    assert [item["id"] for item in variants] == ["A", "B"]
    assert variants[0]["title"] != variants[1]["title"]


def test_creates_experiment_assets(tmp_path):
    path = create_experiment("The ocean mystery", str(tmp_path), "exp-test")
    root = tmp_path / "experiments" / "exp-test"
    data = json.loads(path.read_text())
    assert data["winner"] is None
    assert len(data["variants"]) == 2
    assert (root / "thumbnail-A.svg").exists()
    assert (root / "thumbnail-B.svg").exists()
