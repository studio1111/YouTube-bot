from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CostEvent:
    stage: str
    provider: str
    amount_usd: float
    units: float = 1.0
    note: str = ""


class CostLedger:
    def __init__(self, path: str | Path = "runtime/costs.jsonl") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, event: CostEvent) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event.__dict__) + "\n")

    def total(self) -> float:
        if not self.path.exists():
            return 0.0
        return round(sum(json.loads(line).get("amount_usd", 0.0) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()), 4)

    def by_stage(self) -> dict[str, float]:
        totals: dict[str, float] = {}
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                item = json.loads(line)
                totals[item["stage"]] = round(totals.get(item["stage"], 0.0) + float(item["amount_usd"]), 4)
        return totals
