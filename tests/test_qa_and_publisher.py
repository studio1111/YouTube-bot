import json
import pytest
from yt_agent.publisher import prepare_publish_package
from yt_agent.qa import evaluate_episode_qa
from yt_agent.vertical_slice import build_video


def test_full_vertical_slice_qa_and_publish_prep(tmp_path):
    output = build_video("How solar sails work", runtime_dir=str(tmp_path), episode_id="ep-solar")
    episode_dir = output.parent

    qa = evaluate_episode_qa(episode_dir)
    assert qa["passed"] is True
    assert qa["checks"]["subtitles_exist"] is True
    assert qa["checks"]["seo_exists"] is True

    with pytest.raises(ValueError, match="Human approval"):
        prepare_publish_package(episode_dir, approved_by="")

    pkg_path = prepare_publish_package(
        episode_dir,
        approved_by="speinnov",
        publish_at="2026-10-25T18:00:00Z",
    )
    pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
    assert pkg["youtube_insert_body"]["status"]["privacyStatus"] == "private"
    assert pkg["youtube_insert_body"]["status"]["publishAt"] == "2026-10-25T18:00:00Z"
    assert pkg["checksums"]["manifest_sha256"]
