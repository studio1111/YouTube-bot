import json
from datetime import datetime, timezone

from yt_agent.costs import CostEvent, CostLedger
from yt_agent.dashboard import build_dashboard
from yt_agent.runtime import RunLedger
from yt_agent.scheduler import due_entries, write_schedule
from yt_agent.retry import with_retry


def test_run_ledger_is_idempotent(tmp_path):
    ledger = RunLedger(tmp_path / "agent.db")
    assert ledger.start("r1", "render", {"topic": "x"}) is True
    ledger.finish("r1", "succeeded", "video.mp4")
    assert ledger.start("r1", "render", {"topic": "x"}) is False


def test_cost_dashboard_and_schedule(tmp_path):
    costs = CostLedger(tmp_path / "costs.jsonl")
    costs.record(CostEvent("render", "local", 0.0))
    assert costs.total() == 0.0
    schedule = tmp_path / "schedule.json"
    write_schedule(schedule, [{"id": "x", "due_at": "2026-10-18T00:00:00Z", "status": "queued"}])
    assert len(due_entries(schedule, datetime(2026, 10, 19, tzinfo=timezone.utc))) == 1
    assert build_dashboard(str(tmp_path)).exists()


def test_retry_eventually_succeeds():
    attempts = {"n": 0}
    def operation():
        attempts["n"] += 1
        if attempts["n"] < 2:
            raise RuntimeError("temporary")
        return "ok"
    assert with_retry(operation, attempts=2, base_delay=0) == "ok"
