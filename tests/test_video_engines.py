import json
import pytest
from yt_agent.vertical_slice import build_video
from yt_agent.video_engines import FREE_VIDEO_MODES


@pytest.mark.parametrize("mode", FREE_VIDEO_MODES)
def test_all_free_video_modes_build_end_to_end(tmp_path, mode):
    out = build_video(
        f"Test topic for {mode}",
        runtime_dir=str(tmp_path),
        episode_id=f"ep-{mode}",
        video_mode=mode,
    )
    ep_dir = out.parent
    manifest = json.loads((ep_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["artifacts"]["video_mode"] == mode
    if mode == "openverse-broll":
        assert (ep_dir / "broll" / "broll_sources.json").exists()
    if mode == "comfyui-workflow":
        assert (ep_dir / "workflows" / "comfyui_workflow.json").exists()
