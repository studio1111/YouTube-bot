import json
from pathlib import Path
import pytest
from yt_agent.publisher import prepare_publish_package
from yt_agent.youtube_publish import release_approval_file


def test_publish_package_requires_video_and_stays_non_public(tmp_path):
    (tmp_path / "manifest.json").write_text(json.dumps({"sources": []}))
    (tmp_path / "seo.json").write_text(json.dumps({"primary_title": "Test", "description": "Test", "tags": [], "category_id": "28"}))
    (tmp_path / "qa_report.json").write_text(json.dumps({"passed": True}))
    (tmp_path / "script.txt").write_text("test")
    (tmp_path / "video.mp4").write_bytes(b"fake")
    package = prepare_publish_package(tmp_path, approved_by="speinnov", publish_at="2026-10-25T18:00:00Z")
    data = json.loads(package.read_text())
    assert data["youtube_insert_body"]["status"]["privacyStatus"] == "private"
    assert "public" not in data["youtube_insert_body"]["status"]["privacyStatus"]


def test_release_needs_private_upload(tmp_path):
    with pytest.raises(FileNotFoundError):
        release_approval_file(tmp_path, "speinnov")
