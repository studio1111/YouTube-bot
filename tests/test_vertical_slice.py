import json
from yt_agent.vertical_slice import build_video, generate_idea


def test_idea_is_deterministic():
    assert generate_idea()["title"] == "Why the sky changes color"


def test_vertical_slice_writes_artifacts(tmp_path):
    output = build_video("A test story", str(tmp_path), "ep-test")
    root = tmp_path / "episodes" / "ep-test" / "v1"
    assert output.exists()
    assert (root / "script.txt").exists()
    assert len(list((root / "frames").glob("*.ppm"))) == 5
    manifest = json.loads((root / "manifest.json").read_text())
    assert manifest["topic"] == "A test story"
