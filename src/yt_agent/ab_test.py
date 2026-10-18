from __future__ import annotations

import json
import re
from pathlib import Path


def title_variants(topic: str) -> list[dict[str, str]]:
    clean = topic.strip().rstrip(".")
    return [
        {"id": "A", "title": f"The Truth About {clean}"},
        {"id": "B", "title": f"Nobody Explains {clean} Like This"},
    ]


def _escape(value: str) -> str:
    return (value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def _svg(title: str, variant: str, accent: str) -> str:
    words = re.findall(r"\S+", title)
    lines = [" ".join(words[i:i + 4]) for i in range(0, len(words), 4)] or [title]
    text = "".join(
        f'<text x="80" y="{210 + i * 72}" class="headline">{_escape(line)}</text>'
        for i, line in enumerate(lines[:4])
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#07152f"/><stop offset="1" stop-color="{accent}"/></linearGradient></defs>
<rect width="1280" height="720" fill="url(#bg)"/><circle cx="1080" cy="150" r="180" fill="#ffffff" opacity=".10"/>
<rect x="70" y="70" width="120" height="48" rx="24" fill="#ffffff" opacity=".18"/><text x="105" y="103" class="badge">TEST {variant}</text>
{text}<text x="80" y="650" class="footer">YOUTUBE CHANNEL AGENT</text>
<style>.headline{{font:700 54px Arial,sans-serif;fill:#fff}}.badge{{font:700 20px Arial,sans-serif;fill:#fff}}.footer{{font:600 20px Arial,sans-serif;fill:#bfe8ff;letter-spacing:4px}}</style>
</svg>'''


def create_experiment(topic: str, runtime_dir: str = "runtime", experiment_id: str = "exp-001") -> Path:
    root = Path(runtime_dir) / "experiments" / experiment_id
    root.mkdir(parents=True, exist_ok=True)
    variants = title_variants(topic)
    colors = {"A": "#0b5680", "B": "#6b247e"}
    for item in variants:
        (root / f"thumbnail-{item['id']}.svg").write_text(
            _svg(item["title"], item["id"], colors[item["id"]]), encoding="utf-8"
        )
    manifest = {
        "experiment_id": experiment_id,
        "topic": topic,
        "metric": "click_through_rate",
        "variants": [
            {**item, "thumbnail": f"thumbnail-{item['id']}.svg", "status": "ready"}
            for item in variants
        ],
        "winner": None,
        "decision_rule": "Choose the variant with the highest CTR after equal traffic and at least 100 impressions each.",
        "created_by": "local-deterministic-generator",
    }
    path = root / "experiment.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return path
