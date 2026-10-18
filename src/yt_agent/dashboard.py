from __future__ import annotations

import json
from html import escape
from pathlib import Path

from .costs import CostLedger
from .runtime import RunLedger


def build_dashboard(runtime_dir: str = "runtime") -> Path:
    root = Path(runtime_dir)
    runs = RunLedger(root / "agent.db").recent()
    costs = CostLedger(root / "costs.jsonl")
    rows = "".join(f"<tr><td>{escape(str(r['workflow']))}</td><td>{escape(str(r['status']))}</td><td>{escape(str(r['updated_at']))}</td></tr>" for r in runs)
    html = f"""<!doctype html><meta charset='utf-8'><title>YouTube Agent Dashboard</title>
    <style>body{{font:16px system-ui;background:#10131a;color:#f4f1ea;max-width:1000px;margin:40px auto;padding:0 20px}}.card{{background:#1b2030;border:1px solid #343b52;border-radius:16px;padding:20px;margin:16px 0}}.accent{{color:#d7ff64}}table{{width:100%;border-collapse:collapse}}td{{padding:10px;border-bottom:1px solid #343b52}}</style>
    <h1>YouTube Agent <span class='accent'>Control Room</span></h1><div class='card'><b>Total tracked cost</b><h2>${costs.total():.2f}</h2></div><div class='card'><h2>Recent runs</h2><table><tr><th>Workflow</th><th>Status</th><th>Updated</th></tr>{rows}</table></div>"""
    out = root / "dashboard.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out
