from __future__ import annotations

import html
import json
from pathlib import Path


def _initials(channel_name: str) -> str:
    parts = [p[0].upper() for p in channel_name.split() if p]
    return "".join(parts[:3]) or "YT"


def generate_logo_svg(channel_name: str, accent: str = "#00E5FF", bg: str = "#0B1021") -> str:
    badge = html.escape(_initials(channel_name))
    safe_name = html.escape(channel_name)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800" viewBox="0 0 800 800">
  <defs>
    <linearGradient id="logoBg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{bg}"/>
      <stop offset="100%" stop-color="#1B2845"/>
    </linearGradient>
  </defs>
  <rect width="800" height="800" rx="180" fill="url(#logoBg)"/>
  <circle cx="400" cy="360" r="210" fill="none" stroke="{accent}" stroke-width="18"/>
  <polygon points="355,270 355,450 500,360" fill="{accent}"/>
  <text x="400" y="650" text-anchor="middle" fill="#FFFFFF" font-family="sans-serif" font-size="76" font-weight="bold">{badge}</text>
  <title>{safe_name} Logo</title>
</svg>
"""


def generate_banner_svg(
    channel_name: str,
    tagline: str,
    accent: str = "#00E5FF",
    bg: str = "#0B1021",
) -> str:
    safe_name = html.escape(channel_name)
    safe_tagline = html.escape(tagline)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="2560" height="1440" viewBox="0 0 2560 1440">
  <defs>
    <linearGradient id="bannerBg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{bg}"/>
      <stop offset="100%" stop-color="#142952"/>
    </linearGradient>
  </defs>
  <rect width="2560" height="1440" fill="url(#bannerBg)"/>
  <rect x="507" y="508" width="1546" height="423" rx="28" fill="#0F172A" stroke="{accent}" stroke-width="6"/>
  <text x="1280" y="690" text-anchor="middle" fill="#FFFFFF" font-family="sans-serif" font-size="92" font-weight="bold">{safe_name}</text>
  <text x="1280" y="795" text-anchor="middle" fill="{accent}" font-family="sans-serif" font-size="44">{safe_tagline}</text>
</svg>
"""


def generate_watermark_svg(channel_name: str, accent: str = "#00E5FF") -> str:
    badge = html.escape(_initials(channel_name))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="150" height="150" viewBox="0 0 150 150">
  <rect width="150" height="150" rx="30" fill="#0B1021" fill-opacity="0.82" stroke="{accent}" stroke-width="4"/>
  <text x="75" y="95" text-anchor="middle" fill="#FFFFFF" font-family="sans-serif" font-size="52" font-weight="bold">{badge}</text>
</svg>
"""


def generate_poster_svg(title: str, subtitle: str, accent: str = "#00E5FF") -> str:
    safe_title = html.escape(title)
    safe_sub = html.escape(subtitle)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">
  <rect width="1080" height="1920" fill="#0B1021"/>
  <rect x="70" y="120" width="940" height="1680" rx="42" fill="#131D38" stroke="{accent}" stroke-width="8"/>
  <text x="540" y="860" text-anchor="middle" fill="#FFFFFF" font-family="sans-serif" font-size="68" font-weight="bold">{safe_title}</text>
  <text x="540" y="980" text-anchor="middle" fill="{accent}" font-family="sans-serif" font-size="40">{safe_sub}</text>
</svg>
"""


def build_brand_kit(
    channel_name: str,
    tagline: str = "New science & technology stories every week",
    runtime_dir: str = "runtime",
    accent: str = "#00E5FF",
) -> Path:
    slug = "-".join(channel_name.lower().split())[:40] or "channel"
    out_dir = Path(runtime_dir) / "branding" / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "logo.svg").write_text(generate_logo_svg(channel_name, accent=accent), encoding="utf-8")
    (out_dir / "banner.svg").write_text(generate_banner_svg(channel_name, tagline, accent=accent), encoding="utf-8")
    (out_dir / "watermark.svg").write_text(generate_watermark_svg(channel_name, accent=accent), encoding="utf-8")
    (out_dir / "poster.svg").write_text(generate_poster_svg(channel_name, tagline, accent=accent), encoding="utf-8")
    manifest = {
        "channel_name": channel_name,
        "tagline": tagline,
        "accent": accent,
        "assets": {
            "logo": "logo.svg",
            "banner": "banner.svg",
            "watermark": "watermark.svg",
            "poster": "poster.svg",
        },
    }
    manifest_path = out_dir / "brand_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest_path
