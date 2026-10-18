from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def write_schedule(schedule_file: str | Path, entries: list[dict[str, str]]) -> Path:
    path = Path(schedule_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"updated_at": datetime.now(timezone.utc).isoformat(), "entries": entries}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def due_entries(schedule_file: str | Path, now: datetime | None = None) -> list[dict[str, str]]:
    now = now or datetime.now(timezone.utc)
    data = json.loads(Path(schedule_file).read_text(encoding="utf-8"))
    due = []
    for item in data.get("entries", []):
        due_at = datetime.fromisoformat(item["due_at"].replace("Z", "+00:00"))
        if due_at <= now and item.get("status", "queued") == "queued":
            due.append(item)
    return due
