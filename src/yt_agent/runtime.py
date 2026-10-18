from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class RunLedger:
    """Tiny SQLite run ledger for resumability, idempotency, and auditability."""

    def __init__(self, path: str | Path = "runtime/agent.db") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS runs (
              run_id TEXT PRIMARY KEY, workflow TEXT NOT NULL, status TEXT NOT NULL,
              input_hash TEXT NOT NULL, output_path TEXT, error TEXT,
              created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_runs_workflow_status ON runs(workflow, status);
            """)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        db = sqlite3.connect(self.path)
        try:
            yield db
            db.commit()
        finally:
            db.close()

    @staticmethod
    def input_hash(payload: object) -> str:
        raw = json.dumps(payload, sort_keys=True, default=str).encode()
        return hashlib.sha256(raw).hexdigest()

    def start(self, run_id: str, workflow: str, payload: object) -> bool:
        now = utc_now()
        digest = self.input_hash(payload)
        with self.connect() as db:
            existing = db.execute("SELECT status, input_hash FROM runs WHERE run_id = ?", (run_id,)).fetchone()
            if existing and existing[0] == "succeeded" and existing[1] == digest:
                return False
            db.execute(
                "INSERT OR REPLACE INTO runs(run_id, workflow, status, input_hash, output_path, error, created_at, updated_at) VALUES(?,?,?,?,?,?,COALESCE((SELECT created_at FROM runs WHERE run_id=?),?),?)",
                (run_id, workflow, "running", digest, None, None, run_id, now, now),
            )
        return True

    def finish(self, run_id: str, status: str, output_path: str | None = None, error: str | None = None) -> None:
        with self.connect() as db:
            db.execute("UPDATE runs SET status=?, output_path=?, error=?, updated_at=? WHERE run_id=?", (status, output_path, error, utc_now(), run_id))

    def recent(self, limit: int = 20) -> list[dict[str, str | None]]:
        with self.connect() as db:
            rows = db.execute("SELECT run_id, workflow, status, output_path, error, created_at, updated_at FROM runs ORDER BY updated_at DESC LIMIT ?", (limit,)).fetchall()
        keys = ["run_id", "workflow", "status", "output_path", "error", "created_at", "updated_at"]
        return [dict(zip(keys, row)) for row in rows]
