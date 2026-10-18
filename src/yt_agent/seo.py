from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "what", "why", "how",
    "into", "your", "about", "when", "where", "who", "will", "have", "more",
}


def _format_timestamp(seconds: int) -> str:
    mins, secs = divmod(max(0, int(seconds)), 60)
    hrs, mins = divmod(mins, 60)
    if hrs:
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"


def extract_keywords(topic: str, script_text: str, max_tags: int = 12) -> list[str]:
    combined = f"{topic} {script_text}".lower()
    words = re.findall(r"[a-z0-9]{3,}", combined)
    counts: dict[str, int] = {}
    for w in words:
        if w in STOPWORDS:
            continue
        counts[w] = counts.get(w, 0) + 1
    ranked = [w for w, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))]
    base_tags = [topic.strip().lower()]
    for word in ranked:
        if word not in base_tags:
            base_tags.append(word)
        if len(base_tags) >= max_tags:
            break
    return base_tags


def build_chapters(paragraphs: list[str], seconds_per_section: int = 15) -> list[dict[str, str]]:
    chapters: list[dict[str, str]] = []
    current = 0
    for idx, para in enumerate(paragraphs):
        headline = para.split(".")[0].strip()[:48] or f"Part {idx + 1}"
        if idx == 0:
            headline = f"Intro: {headline}"
        chapters.append({"timestamp": _format_timestamp(current), "title": headline})
        current += seconds_per_section
    return chapters


def generate_seo_metadata(
    topic: str,
    script_text: str,
    sources: list[str] | None = None,
    seconds_per_section: int = 15,
) -> dict[str, Any]:
    clean_topic = topic.strip().rstrip(".")
    paragraphs = [p.strip() for p in script_text.split("\n\n") if p.strip()]
    chapters = build_chapters(paragraphs or [clean_topic], seconds_per_section=seconds_per_section)
    tags = extract_keywords(clean_topic, script_text)
    hashtags = [f"#{re.sub(r'[^a-zA-Z0-9]', '', t.title())}" for t in tags[:4] if t]
    chapter_lines = "\n".join(f"{c['timestamp']} {c['title']}" for c in chapters)
    source_lines = "\n".join(f"- {s}" for s in (sources or ["local://generated"]))
    description = (
        f"{paragraphs[0] if paragraphs else clean_topic}\n\n"
        f"Chapters:\n{chapter_lines}\n\n"
        f"Sources & References:\n{source_lines}\n\n"
        f"{' '.join(hashtags)}"
    ).strip()
    return {
        "primary_title": f"{clean_topic}: How It Really Works"[:100],
        "alt_titles": [
            f"The Surprising Truth About {clean_topic}"[:100],
            f"{clean_topic} Explained in Plain English"[:100],
        ],
        "description": description[:4900],
        "tags": tags,
        "hashtags": hashtags,
        "chapters": chapters,
        "category_id": "28",
    }


def write_seo_package(
    episode_dir: str | Path,
    topic: str,
    script_text: str,
    sources: list[str] | None = None,
) -> Path:
    root = Path(episode_dir)
    root.mkdir(parents=True, exist_ok=True)
    seo_data = generate_seo_metadata(topic, script_text, sources=sources)
    out = root / "seo.json"
    out.write_text(json.dumps(seo_data, indent=2), encoding="utf-8")
    return out
