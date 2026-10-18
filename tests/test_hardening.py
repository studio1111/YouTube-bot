import json
from yt_agent.health import check_environment, write_health_report
from yt_agent.provenance import write_provenance


def test_health_report_is_safe_and_structured(tmp_path):
    report = check_environment(str(tmp_path))
    assert "checks" in report
    assert "YOUTUBE_CLIENT_SECRET_FILE" not in json.dumps(report)
    assert write_health_report(str(tmp_path)).exists()


def test_provenance_hashes_episode_files(tmp_path):
    (tmp_path / "video.mp4").write_bytes(b"sample")
    out = write_provenance(tmp_path)
    data = json.loads(out.read_text())
    assert data["schema"] == "yt-agent.provenance.v1"
    assert data["files"][0]["sha256"]
