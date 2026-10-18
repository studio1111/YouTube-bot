from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from typing import Any

from .ab_test import create_experiment
from .branding import build_brand_kit
from .publisher import prepare_publish_package
from .qa import evaluate_episode_qa
from .trends import discover_trends
from .vertical_slice import build_video


def try_ollama_idea(topic: str, ollama_url: str = "http://localhost:11434", model: str = "qwen3:4b") -> dict[str, Any] | None:
    """Attempt local Ollama JSON generation; safely return None if Ollama is not running."""
    prompt = (
        f"Create a concise YouTube short script about '{topic}'. "
        "Return strict JSON with keys: title (string), hook (string), beats (list of 3 strings), close (string)."
    )
    payload = json.dumps({"model": model, "prompt": prompt, "format": "json", "stream": False}).encode("utf-8")
    req = urllib.request.Request(
        f"{ollama_url.rstrip('/')}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=3) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        idea = json.loads(body.get("response", "{}"))
        if idea.get("title") and idea.get("hook") and isinstance(idea.get("beats"), list):
            return idea
    except Exception:
        return None
    return None


def run_autopilot(
    niche: str,
    channel_name: str = "Deep Cosmos",
    episode_id: str = "ep-auto-001",
    runtime_dir: str = "runtime",
    approved_by: str | None = None,
    publish_at: str | None = None,
) -> Path:
    """Run the complete channel pipeline in one command: trends -> branding -> episode -> A/B test -> QA -> optional publish prep."""
    trends_path = discover_trends(niche, runtime_dir=runtime_dir)
    trends_data = json.loads(trends_path.read_text(encoding="utf-8"))
    top_pick = (trends_data.get("top_pick") or {}).get("title") or niche

    brand_manifest = build_brand_kit(channel_name, runtime_dir=runtime_dir)
    video_output = build_video(top_pick, runtime_dir=runtime_dir, episode_id=episode_id)
    episode_dir = video_output.parent
    ab_manifest = create_experiment(top_pick, runtime_dir=runtime_dir, experiment_id=f"ab-{episode_id}")
    qa_report = evaluate_episode_qa(episode_dir)

    publish_pkg = None
    if approved_by:
        publish_pkg = str(
            prepare_publish_package(episode_dir, approved_by=approved_by, publish_at=publish_at)
        )

    summary = {
        "niche": niche,
        "selected_topic": top_pick,
        "channel_name": channel_name,
        "episode_id": episode_id,
        "artifacts": {
            "trends": str(trends_path),
            "brand_manifest": str(brand_manifest),
            "episode_dir": str(episode_dir),
            "video": str(video_output),
            "ab_experiment": str(ab_manifest),
            "publish_package": publish_pkg,
        },
        "qa_passed": qa_report["passed"],
        "ready_for_upload": qa_report["ready_for_upload"],
    }
    summary_path = episode_dir / "autopilot_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary_path
