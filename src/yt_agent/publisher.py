from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def prepare_publish_package(
    episode_dir: str | Path,
    approved_by: str | None = None,
    publish_at: str | None = None,
    synthetic_disclosure: bool = True,
    privacy_status: str = "private",
) -> Path:
    if not approved_by or not approved_by.strip():
        raise ValueError("Human approval (`approved_by`) is required before preparing a publish package.")
    if privacy_status not in {"private", "unlisted", "public"}:
        raise ValueError(f"Unsupported privacy_status: {privacy_status}")
    if publish_at and privacy_status != "private":
        raise ValueError("YouTube scheduled `publishAt` requires `privacy_status='private'`.")

    root = Path(episode_dir)
    manifest_path = root / "manifest.json"
    seo_path = root / "seo.json"
    qa_path = root / "qa_report.json"

    if not manifest_path.exists() or not seo_path.exists() or not qa_path.exists():
        raise FileNotFoundError("Episode directory must contain manifest.json, seo.json, and qa_report.json.")

    qa = json.loads(qa_path.read_text(encoding="utf-8"))
    if not qa.get("passed"):
        raise ValueError(f"QA checks did not pass: {qa.get('warnings')}")

    seo = json.loads(seo_path.read_text(encoding="utf-8"))
    status_block: dict[str, Any] = {
        "privacyStatus": privacy_status,
        "selfDeclaredMadeForKids": False,
        "containsSyntheticMedia": bool(synthetic_disclosure),
    }
    if publish_at:
        status_block["publishAt"] = publish_at

    video_path = root / "video.mp4"
    script_path = root / "script.txt"
    package = {
        "prepared_at": datetime.now(timezone.utc).isoformat(),
        "approval": {
            "approved_by": approved_by.strip(),
            "approved_at": datetime.now(timezone.utc).isoformat(),
        },
        "youtube_insert_body": {
            "snippet": {
                "title": seo["primary_title"],
                "description": seo["description"],
                "tags": seo["tags"],
                "categoryId": seo.get("category_id", "28"),
            },
            "status": status_block,
        },
        "checksums": {
            "manifest_sha256": _sha256(manifest_path),
            "seo_sha256": _sha256(seo_path),
            "script_sha256": _sha256(script_path) if script_path.exists() else None,
            "video_sha256": _sha256(video_path) if video_path.exists() else None,
        },
    }
    out = root / "publish_package.json"
    out.write_text(json.dumps(package, indent=2), encoding="utf-8")
    return out
