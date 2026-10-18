import json
from pathlib import Path

from yt_agent.video_engines import FREE_VIDEO_MODES, prepare_visual_assets


def test_all_modes_have_a_routing_contract(tmp_path):
    for mode in FREE_VIDEO_MODES:
        root = tmp_path / mode
        extras = prepare_visual_assets(
            "Quantum batteries",
            ["Hook", "Mechanism", "Close"],
            root / "frames",
            root,
            mode=mode,
        )
        assert extras["video_mode"] == mode
        assert sorted((root / "frames").glob("slide-*.ppm"))
        if mode == "openverse-broll":
            assert (root / "broll" / "broll_sources.json").exists()
        if mode == "comfyui-workflow":
            workflow = json.loads((root / "workflows" / "comfyui_workflow.json").read_text())
            assert workflow["engine"] == "ComfyUI Local Free Workflow"
