from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    digest.update(Path(path).read_bytes())
    return digest.hexdigest()


def build_provenance(episode_dir: str | Path) -> dict[str, Any]:
    root = Path(episode_dir)
    files = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name not in {"provenance.json"}:
            files.append({"path": str(path.relative_to(root)), "sha256": sha256_file(path), "bytes": path.stat().st_size})
    return {"schema": "yt-agent.provenance.v1", "generated_at": datetime.now(timezone.utc).isoformat(), "files": files}


def write_provenance(episode_dir: str | Path) -> Path:
    root = Path(episode_dir)
    out = root / "provenance.json"
    out.write_text(json.dumps(build_provenance(root), indent=2), encoding="utf-8")
    return out
