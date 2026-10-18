from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


def probe_video(video_path: Path) -> dict[str, Any]:
    if not video_path.exists() or video_path.suffix.lower() != ".mp4":
        return {"probed": False, "reason": "mp4 file not present"}
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return {"probed": False, "reason": "ffprobe not installed", "size_bytes": video_path.stat().st_size}
    proc = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration,size:stream=codec_name,width,height",
            "-of",
            "json",
            str(video_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return {"probed": False, "reason": proc.stderr.strip() or "ffprobe error"}
    data = json.loads(proc.stdout or "{}")
    return {"probed": True, "details": data}


def evaluate_episode_qa(episode_dir: str | Path, synthetic_media_disclosed: bool = True) -> dict[str, Any]:
    root = Path(episode_dir)
    manifest_file = root / "manifest.json"
    script_file = root / "script.txt"
    seo_file = root / "seo.json"
    srt_file = root / "captions.srt"
    video_file = root / "video.mp4"

    warnings: list[str] = []
    checks: dict[str, bool] = {}

    checks["manifest_exists"] = manifest_file.exists()
    if not checks["manifest_exists"]:
        warnings.append("Missing manifest.json")

    checks["script_non_empty"] = script_file.exists() and len(script_file.read_text(encoding="utf-8").strip()) >= 40
    if not checks["script_non_empty"]:
        warnings.append("Script is missing or too short (< 40 chars)")

    checks["subtitles_exist"] = srt_file.exists() and "-->" in srt_file.read_text(encoding="utf-8")
    if not checks["subtitles_exist"]:
        warnings.append("Missing valid SRT subtitles (captions.srt)")

    checks["seo_exists"] = seo_file.exists()
    if not checks["seo_exists"]:
        warnings.append("Missing SEO metadata package (seo.json)")

    if manifest_file.exists():
        manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))
        sources = manifest_data.get("sources", [])
        checks["has_provenance_sources"] = bool(sources) and all(
            s.get("url") and s.get("license") for s in sources
        )
    else:
        checks["has_provenance_sources"] = False
    if not checks["has_provenance_sources"]:
        warnings.append("Missing source provenance or license metadata in manifest")

    checks["synthetic_disclosure_set"] = bool(synthetic_media_disclosed)
    if not checks["synthetic_disclosure_set"]:
        warnings.append("Synthetic/altered media disclosure decision is required before publishing")

    video_probe = probe_video(video_file)
    checks["video_rendered"] = video_file.exists() and video_file.stat().st_size > 0
    if not checks["video_rendered"]:
        warnings.append("MP4 video not rendered yet (install FFmpeg or render video.mp4)")

    passed = all(
        [
            checks["manifest_exists"],
            checks["script_non_empty"],
            checks["subtitles_exist"],
            checks["seo_exists"],
            checks["has_provenance_sources"],
            checks["synthetic_disclosure_set"],
        ]
    )
    report = {
        "passed": passed,
        "ready_for_upload": passed and checks["video_rendered"],
        "checks": checks,
        "video_probe": video_probe,
        "warnings": warnings,
    }
    (root / "qa_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
