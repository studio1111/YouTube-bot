from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path
from typing import Any


SCHEMA = {
    "title": "string, max 100 chars",
    "logline": "one sentence",
    "hook": "spoken opening under 25 words",
    "beats": ["5 to 8 numbered beats with concrete visuals"],
    "narration": "full original narration",
    "visual_plan": [{"timecode": "00:00", "visual": "", "source_type": "original|cc0|generated", "rights": ""}],
    "sound_plan": [{"timecode": "00:00", "cue": "", "license": ""}],
    "cta": "non-manipulative call to action",
    "seo": {"title": "", "description": "", "tags": []},
    "risk_flags": ["factual, copyright, privacy, synthetic-media risks"],
    "sources": [{"claim": "", "url": "", "retrieved_at": ""}],
}


def build_prompt(idea: dict[str, Any], audience: str = "curious science and technology viewers", format_name: str = "long-form") -> str:
    return f"""You are an evidence-first YouTube showrunner. Create an original {format_name} episode for {audience}.

IDEA BRIEF:
{json.dumps(idea, ensure_ascii=False, indent=2)}

REQUIREMENTS:
- Return valid JSON only matching this schema: {json.dumps(SCHEMA)}
- Do not copy wording, footage, audio, or distinctive creative expression from source posts.
- Use sources for claims, not as scripts. Mark uncertain claims and ask for human review.
- Every visual must be original, public-domain/CC0/compatible CC, or generated locally; record rights.
- Build a specific hook, escalating beats, visual variety, a clear payoff, and a non-manipulative CTA.
- Add synthetic-media disclosure risk when realistic people, events, places, or voices are involved.
- Never invent statistics, quotes, citations, or product claims.
"""


def _ollama_json(prompt: str, model: str = "qwen3:8b", base_url: str = "http://localhost:11434") -> dict[str, Any] | None:
    payload = json.dumps({"model": model, "prompt": prompt, "format": "json", "stream": False}).encode()
    request = urllib.request.Request(f"{base_url.rstrip('/')}/api/generate", data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode())
        return json.loads(result.get("response", "{}"))
    except Exception:
        return None


def generate_scenario(idea: dict[str, Any], audience: str = "curious science and technology viewers", format_name: str = "long-form", model: str | None = None) -> dict[str, Any]:
    prompt = build_prompt(idea, audience, format_name)
    result = _ollama_json(prompt, model or os.getenv("OLLAMA_MODEL", "qwen3:8b"), os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    if result:
        result["prompt_version"] = "scenario-v1"
        return result
    return {"title": idea.get("title", "Untitled"), "logline": idea.get("story_angle", "Original explainer"), "hook": f"Here is the overlooked mechanism behind {idea.get('title', 'this story') }.", "beats": [], "narration": "", "visual_plan": [], "sound_plan": [], "cta": "Subscribe for the next evidence-backed explainer.", "seo": {"title": idea.get("title", "Untitled"), "description": "Draft requires local Ollama or human writing.", "tags": []}, "risk_flags": ["Scenario generation unavailable; human draft required."], "sources": [], "prompt_version": "scenario-v1"}


def write_scenario(idea: dict[str, Any], runtime_dir: str = "runtime", audience: str = "curious science and technology viewers", format_name: str = "long-form") -> Path:
    root = Path(runtime_dir) / "scenarios"
    root.mkdir(parents=True, exist_ok=True)
    result = generate_scenario(idea, audience, format_name)
    slug = "-".join(str(result.get("title", "scenario")).lower().split())[:50] or "scenario"
    out = root / f"scenario-{slug}.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return out
