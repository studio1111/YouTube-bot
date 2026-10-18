from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def build_calendar(ideas: list[dict[str, Any]], start_date: str, weeks: int = 4) -> list[dict[str, Any]]:
    start = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc)
    rows: list[dict[str, Any]] = []
    for idx in range(max(1, weeks) * 2):
        idea = ideas[idx % len(ideas)] if ideas else {"title": "Needs idea", "stable_id": ""}
        due = start + timedelta(days=idx * 3)
        rows.append({"slot": idx + 1, "due_at": due.isoformat(), "format": "long-form" if idx % 2 == 0 else "short", "idea_id": idea.get("stable_id", ""), "title": idea.get("title", "Needs idea"), "status": "queued"})
    return rows


def write_calendar(ideas_file: str, start_date: str, runtime_dir: str = "runtime", weeks: int = 4) -> Path:
    ideas = json.loads(Path(ideas_file).read_text(encoding="utf-8"))
    rows = build_calendar(ideas.get("items", []), start_date, weeks)
    root = Path(runtime_dir) / "calendar"
    root.mkdir(parents=True, exist_ok=True)
    out = root / "content-calendar.json"
    out.write_text(json.dumps({"schema": "yt-agent.calendar.v1", "entries": rows}, indent=2), encoding="utf-8")
    return out
