from __future__ import annotations

import hashlib
import json
import os
import re
import time
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class TrendItem:
    platform: str
    title: str
    url: str
    published_at: str = ""
    creator: str = ""
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    source_kind: str = "official_api"
    license_status: str = "reference_only"

    @property
    def stable_id(self) -> str:
        return hashlib.sha256(f"{self.platform}|{self.url}|{self.title}".encode()).hexdigest()[:16]


class RateLimiter:
    def __init__(self, requests_per_minute: int = 30) -> None:
        self.delay = 60.0 / max(1, requests_per_minute)
        self.last_request = 0.0

    def wait(self) -> None:
        elapsed = time.monotonic() - self.last_request
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_request = time.monotonic()


def _get_json(url: str, headers: dict[str, str] | None = None, timeout: int = 10) -> dict[str, Any]:
    request = urllib.request.Request(url, headers=headers or {"User-Agent": "yt-agent/0.1"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def youtube_search(query: str, api_key: str | None = None, max_results: int = 25) -> list[TrendItem]:
    key = api_key or os.getenv("YOUTUBE_DATA_API_KEY")
    if not key:
        return []
    params = urllib.parse.urlencode({"part": "snippet", "q": query, "type": "video", "order": "viewCount", "maxResults": min(max_results, 50), "key": key})
    payload = _get_json(f"https://www.googleapis.com/youtube/v3/search?{params}")
    items: list[TrendItem] = []
    for row in payload.get("items", []):
        snippet = row.get("snippet", {})
        video_id = row.get("id", {}).get("videoId", "")
        items.append(TrendItem("youtube", snippet.get("title", ""), f"https://www.youtube.com/watch?v={video_id}", snippet.get("publishedAt", ""), snippet.get("channelTitle", "")))
    return items


def instagram_media(access_token: str | None = None, user_id: str | None = None, max_results: int = 25) -> list[TrendItem]:
    token = access_token or os.getenv("INSTAGRAM_ACCESS_TOKEN")
    account = user_id or os.getenv("INSTAGRAM_USER_ID")
    if not token or not account:
        return []
    fields = "id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count"
    params = urllib.parse.urlencode({"fields": fields, "limit": min(max_results, 100), "access_token": token})
    payload = _get_json(f"https://graph.instagram.com/{account}/media?{params}")
    items: list[TrendItem] = []
    for row in payload.get("data", []):
        caption = row.get("caption", "") or "Instagram post"
        title = caption.split("\n")[0][:160]
        items.append(TrendItem("instagram", title, row.get("permalink", ""), row.get("timestamp", ""), "authorized_account", 0, int(row.get("like_count", 0) or 0), int(row.get("comments_count", 0) or 0)))
    return items


def tiktok_authorized_videos(access_token: str | None = None, max_results: int = 20) -> list[TrendItem]:
    token = access_token or os.getenv("TIKTOK_ACCESS_TOKEN")
    if not token:
        return []
    fields = "id,title,video_description,create_time,share_url,like_count,comment_count,share_count,view_count"
    params = urllib.parse.urlencode({"fields": fields, "max_count": min(max_results, 20)})
    payload = _get_json(f"https://open.tiktokapis.com/v2/video/list/?{params}", headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    items: list[TrendItem] = []
    for row in payload.get("data", {}).get("videos", []):
        title = row.get("title") or row.get("video_description") or "TikTok video"
        items.append(TrendItem("tiktok", title[:160], row.get("share_url", ""), str(row.get("create_time", "")), "authorized_account", int(row.get("view_count", 0) or 0), int(row.get("like_count", 0) or 0), int(row.get("comment_count", 0) or 0), int(row.get("share_count", 0) or 0)))
    return items


def _tokenize(text: str) -> set[str]:
    return {w for w in re.findall(r"[\w-]{3,}", text.lower()) if w not in {"the", "and", "for", "with", "this", "that", "from", "your", "why", "how"}}


def dedupe_items(items: Iterable[TrendItem]) -> list[TrendItem]:
    result: list[TrendItem] = []
    seen_urls: set[str] = set()
    seen_tokens: list[set[str]] = []
    for item in items:
        if not item.title.strip():
            continue
        tokens = _tokenize(item.title)
        if item.url and item.url in seen_urls:
            continue
        if any(len(tokens & prior) / max(1, len(tokens | prior)) >= 0.80 for prior in seen_tokens):
            continue
        result.append(item)
        if item.url:
            seen_urls.add(item.url)
        seen_tokens.append(tokens)
    return result


def score_item(item: TrendItem, niche: str = "") -> float:
    words = _tokenize(item.title)
    score = 20.0
    if niche and _tokenize(niche) & words:
        score += 25.0
    if 5 <= len(words) <= 14:
        score += 15.0
    score += min(25.0, (item.likes + 2 * item.comments + 3 * item.shares) / 1000)
    if item.views:
        score += min(15.0, item.views / 1_000_000 * 5)
    return round(min(score, 100.0), 2)


def extract_hooks(items: Iterable[TrendItem], limit: int = 20) -> list[dict[str, Any]]:
    hooks: list[dict[str, Any]] = []
    patterns = [(r"^why\\b", "why-question"), (r"^how\\b", "how-explainer"), (r"\\bvs\\b|versus", "comparison"), (r"secret|hidden|nobody", "curiosity-gap"), (r"what\\b", "what-question")]
    for item in items:
        normalized = " ".join(item.title.split())
        style = "direct-claim"
        for pattern, label in patterns:
            if re.search(pattern, normalized, flags=re.I):
                style = label
                break
        hooks.append({"platform": item.platform, "title": normalized, "hook_style": style, "source_url": item.url, "license_status": item.license_status})
    return hooks[:limit]


def rank_items(items: Iterable[TrendItem], niche: str, limit: int = 20) -> list[dict[str, Any]]:
    ranked = []
    for item in dedupe_items(items):
        ranked.append({"stable_id": item.stable_id, "score": score_item(item, niche), **asdict(item)})
    ranked.sort(key=lambda row: (-row["score"], row["title"]))
    return ranked[:limit]


def collect_platform_ideas(niche: str, max_results: int = 20) -> list[TrendItem]:
    all_items: list[TrendItem] = []
    all_items.extend(youtube_search(niche, max_results=max_results))
    all_items.extend(instagram_media(max_results=max_results))
    all_items.extend(tiktok_authorized_videos(max_results=max_results))
    return all_items


def build_idea_report(niche: str, runtime_dir: str = "runtime", items: list[TrendItem] | None = None) -> Path:
    if items is None:
        items = collect_platform_ideas(niche)
    ranked = rank_items(items, niche)
    hooks = extract_hooks(dedupe_items(items))
    root = Path(runtime_dir) / "ideas"
    root.mkdir(parents=True, exist_ok=True)
    slug = "-".join(niche.lower().split())[:50] or "general"
    report = {"schema": "yt-agent.idea-intelligence.v1", "generated_at": datetime.now(timezone.utc).isoformat(), "niche": niche, "items": ranked, "hook_patterns": hooks, "platforms_seen": sorted({x["platform"] for x in ranked}), "rights_note": "References inform original scripts; source videos are not copied or downloaded."}
    out = root / f"idea-report-{slug}.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return out
