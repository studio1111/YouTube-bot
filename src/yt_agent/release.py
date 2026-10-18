from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REQUIRED_FILES = ("manifest.json", "script.txt", "seo.json", "captions.srt", "captions.vtt", "qa_report.json", "provenance.json", "publish_package.json")


def validate_release(episode_dir: str | Path) -> dict[str, Any]:
    root = Path(episode_dir)
    missing = [name for name in REQUIRED_FILES if not (root / name).exists()]
    qa = json.loads((root / "qa_report.json").read_text()) if (root / "qa_report.json").exists() else {}
    package = json.loads((root / "publish_package.json").read_text()) if (root / "publish_package.json").exists() else {}
    status = package.get("youtube_insert_body", {}).get("status", {})
    checks = {
        "required_files": not missing,
        "qa_passed": qa.get("passed") is True,
        "private_or_unlisted": status.get("privacyStatus") in {"private", "unlisted"},
        "human_approval": bool(package.get("approval", {}).get("approved_by")),
        "video_present": (root / "video.mp4").exists(),
    }
    return {"ready": all(checks.values()), "checks": checks, "missing": missing, "warnings": qa.get("warnings", [])}


def write_release_report(episode_dir: str | Path) -> Path:
    root = Path(episode_dir)
    report = validate_release(root)
    out = root / "release_report.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return out
