from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any


def check_environment(runtime_dir: str = "runtime") -> dict[str, Any]:
    root = Path(runtime_dir)
    checks = {
        "python": True,
        "ffmpeg": bool(shutil.which("ffmpeg")),
        "ffprobe": bool(shutil.which("ffprobe")),
        "runtime_writable": root.exists() or root.parent.exists(),
        "youtube_credentials_configured": bool(__import__("os").getenv("YOUTUBE_CLIENT_SECRET_FILE")),
        "telegram_configured": bool(__import__("os").getenv("TELEGRAM_BOT_TOKEN") and __import__("os").getenv("TELEGRAM_CHAT_ID")),
        "smtp_configured": bool(__import__("os").getenv("SMTP_HOST") and __import__("os").getenv("SMTP_USERNAME")),
    }
    return {"checks": checks, "warnings": [name for name, ok in checks.items() if not ok]}


def write_health_report(runtime_dir: str = "runtime") -> Path:
    root = Path(runtime_dir)
    root.mkdir(parents=True, exist_ok=True)
    out = root / "health.json"
    out.write_text(json.dumps(check_environment(runtime_dir), indent=2), encoding="utf-8")
    return out
