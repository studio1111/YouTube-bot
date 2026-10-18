from __future__ import annotations

import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_FEEDS = [
    "https://hnrss.org/frontpage",
    "https://www.reddit.com/r/science/.rss",
]


def parse_rss_xml(xml_text: str, source_url: str = "rss://feed") -> list[dict[str, str]]:
    root = ET.fromstring(xml_text)
    items: list[dict[str, str]] = []
    for elem in root.findall(".//item"):
        title = (elem.findtext("title") or "").strip()
        link = (elem.findtext("link") or source_url).strip()
        if title:
            items.append({"title": title, "url": link, "source": source_url})
    if not items:
        for elem in root.findall(".//{http://www.w3.org/2005/Atom}entry"):
            title = (elem.findtext("{http://www.w3.org/2005/Atom}title") or "").strip()
            link_elem = elem.find("{http://www.w3.org/2005/Atom}link")
            link = (link_elem.attrib.get("href") if link_elem is not None else source_url) or source_url
            if title:
                items.append({"title": title, "url": link.strip(), "source": source_url})
    return items


def score_idea(title: str, niche_keywords: list[str] | None = None) -> float:
    words = title.lower().split()
    score = 50.0
    if 5 <= len(words) <= 14:
        score += 15.0
    hooks = {"why", "how", "secret", "hidden", "future", "new", "discover", "explained", "what", "first"}
    score += 8.0 * sum(1 for w in words if w.strip("?:!.,") in hooks)
    if niche_keywords:
        for kw in niche_keywords:
            if kw.lower() in title.lower():
                score += 12.0
    return round(min(score, 100.0), 2)


def rank_topics(
    candidates: list[dict[str, str]],
    niche_keywords: list[str] | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    seen: set[str] = set()
    scored: list[dict[str, Any]] = []
    for item in candidates:
        title = item.get("title", "").strip()
        key = title.lower()
        if not title or key in seen:
            continue
        seen.add(key)
        scored.append(
            {
                "title": title,
                "url": item.get("url", "local://seed"),
                "source": item.get("source", "seed"),
                "score": score_idea(title, niche_keywords),
                "story_angle": f"Uncover the surprising mechanism and real-world impact behind: {title}",
            }
        )
    scored.sort(key=lambda x: (-x["score"], x["title"]))
    return scored[:limit]


def fetch_searxng(query: str, searxng_url: str, timeout: int = 8) -> list[dict[str, str]]:
    params = urllib.parse.urlencode({"q": query, "format": "json"})
    url = f"{searxng_url.rstrip('/')}/search?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "yt-agent/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    results = []
    for row in payload.get("results", [])[:15]:
        title = (row.get("title") or "").strip()
        link = (row.get("url") or url).strip()
        if title:
            results.append({"title": title, "url": link, "source": "searxng"})
    return results


def discover_trends(
    niche: str,
    runtime_dir: str = "runtime",
    feeds: list[str] | None = None,
    searxng_url: str | None = None,
    offline_seeds: list[str] | None = None,
) -> Path:
    candidates: list[dict[str, str]] = []
    keywords = [w for w in niche.split() if len(w) > 2]
    if offline_seeds:
        for seed in offline_seeds:
            candidates.append({"title": seed, "url": "local://seed", "source": "offline_seed"})
    for feed_url in feeds or []:
        try:
            req = urllib.request.Request(feed_url, headers={"User-Agent": "yt-agent/0.1"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                xml_text = resp.read().decode("utf-8", errors="replace")
            candidates.extend(parse_rss_xml(xml_text, source_url=feed_url))
        except Exception:
            continue
    if searxng_url:
        try:
            candidates.extend(fetch_searxng(niche, searxng_url))
        except Exception:
            pass
    if not candidates:
        candidates = [
            {"title": f"Why {niche} is changing faster than most people think", "url": "local://fallback", "source": "fallback"},
            {"title": f"How {niche} actually works under the hood", "url": "local://fallback", "source": "fallback"},
            {"title": f"What everyone gets wrong about {niche}", "url": "local://fallback", "source": "fallback"},
        ]
    ranked = rank_topics(candidates, niche_keywords=keywords)
    out_dir = Path(runtime_dir) / "trends"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = "-".join(niche.lower().split())[:40] or "general"
    out_file = out_dir / f"trends-{slug}.json"
    report = {
        "niche": niche,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "top_pick": ranked[0] if ranked else None,
        "ideas": ranked,
    }
    out_file.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return out_file
