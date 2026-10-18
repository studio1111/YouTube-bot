import json
from yt_agent.pipeline import EpisodePipeline


def test_create_manifest(tmp_path):
    path = EpisodePipeline(str(tmp_path)).create("A science story", "ep-test")
    data = json.loads(path.read_text())
    assert data["episode_id"] == "ep-test"
    assert data["topic"] == "A science story"
    assert data["state"] == "idea"
