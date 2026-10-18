# YouTube Channel Agent

A 100% free, local-first, open-source automation suite for running a YouTube channel end-to-end: trend discovery, ideation, scripting, subtitles (SRT/VTT), SEO optimization, channel branding (logo, banner, poster, watermark), deterministic frame/video rendering, A/B thumbnail & title experiments, YouTube Analytics evaluation, Telegram/SMTP alerts, QA compliance checks, and human-approved private upload packaging.

## End-to-End Quickstart

```bash
pip install -e '.[dev]'

# 1. Discover & rank trending topics in your niche
yt-agent trends --niche "quantum computing"

# 2. Build a full channel Brand Kit (Logo, Banner, Watermark, Shorts Poster)
yt-agent branding --channel-name "Deep Cosmos" --tagline "Weekly Space & Physics"

# 3. Run the full vertical slice (Script + SRT/VTT Subtitles + SEO + Slides + MP4 + QA)
yt-agent run --topic "Why the sky changes color" --episode-id ep-001

# 4. Run QA checks or prepare a human-approved Private YouTube Upload package
yt-agent qa --episode-dir runtime/episodes/ep-001/v1
yt-agent publish-prep --episode-dir runtime/episodes/ep-001/v1 --approved-by "speinnov" --publish-at "2026-10-25T18:00:00Z"

# 5. Generate A/B Title & Thumbnail experiments and evaluate with YouTube Analytics
yt-agent ab-test --topic "Why the sky changes color" --experiment-id sky-001
yt-agent analytics --experiment-file runtime/experiments/sky-001/experiment.json --notify telegram email
```

## Included Modules (`src/yt_agent/`)

| Module | Capability |
|---|---|
| `trends.py` | RSS/Atom & SearXNG trend harvesting, curiosity hook scoring, and story angle ranking |
| `branding.py` | Deterministic SVG Channel Logo, YouTube safe-area Banner (2560x1440), Shorts Poster, and Watermark |
| `vertical_slice.py` | End-to-end episode builder: idea, script, subtitles, SEO, frames, FFmpeg MP4 render, and QA |
| `subtitles.py` | Timed caption segmentation and `.srt` / `.vtt` subtitle generation |
| `seo.py` | Primary/alternate titles, keyword extraction, chapters, hashtags, and YouTube description builder |
| `qa.py` | Pre-publish quality gate (`ffprobe`, subtitle verification, source provenance, synthetic media disclosure) |
| `publisher.py` | Human-gated private upload & `publishAt` scheduling manifest with SHA-256 artifact checksums |
| `ab_test.py` | A/B title & SVG thumbnail generator with minimum-impression winner selection |
| `analytics.py` | Read-only YouTube Analytics OAuth client, CTR winner calculation, and incomplete-data warning engine |
| `notifications.py` | Telegram Bot API and SMTP email alert dispatchers |

## Free & Open-Source Stack

| Layer | Default Free Tool | Optional Local Upgrade |
|---|---|---|
| Orchestration | Python CLI + JSON manifests | Temporal OSS / cron |
| LLM Ideation & Script | Deterministic local templates | Ollama (`qwen3` / `llama3`) |
| Trend Research | RSS/Atom feeds + SearXNG | YouTube Data API v3 |
| Subtitles & Captions | Timed script segmenter (`.srt` / `.vtt`) | `faster-whisper` / `whisper.cpp` |
| Voice / TTS | Optional audio track muxing | `Kokoro-82M` / `Piper` |
| Visuals & Branding | Pure SVG / PPM + FFmpeg | `ComfyUI` + `FLUX.1 Schnell` |
| Analytics & Alerts | YouTube Analytics API + Telegram/SMTP | ClickUp Super Agent (`Notification Nudge Nolan`) |

## Guardrails & YouTube Policy Compliance

- **Untrusted research isolation:** External feeds and pages are treated purely as data, never executable instructions.
- **Provenance ledger:** Every episode records its sources and licenses in `manifest.json`.
- **Synthetic media disclosure:** `qa.py` and `publisher.py` enforce explicit disclosure flags for AI-assisted content.
- **Human-in-the-loop publishing:** `publish-prep` requires `--approved-by`, defaults to `private`, and verifies SHA-256 digests before upload.
