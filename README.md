# YouTube Channel Agent

A 100% free, local-first, open-source automation suite for running a YouTube channel end-to-end: trend discovery, ideation, scripting, subtitles (SRT/VTT), SEO optimization, channel branding, deterministic and AI-ready video rendering, A/B testing, YouTube Analytics, alerts, QA, and human-approved private upload packaging.

## Phone-first Colab benchmark

No computer? Open the [mobile benchmark directly in Google Colab](https://colab.research.google.com/github/studio1111/YouTube-bot/blob/main/colab/yt_agent_mobile_benchmark.ipynb), tap **Runtime → Run all**, and send back `mobile-render-benchmark.json`. It needs no terminal, API key, GitHub token, YouTube OAuth, Telegram, or SMTP credentials. Full instructions: [`docs/colab-actions-bridge.md`](docs/colab-actions-bridge.md).

## End-to-End Quickstart

```bash
pip install -e '.[dev]'
yt-agent ideas --niche "quantum computing"
yt-agent scenario --idea-file runtime/ideas/idea-report-quantum-computing.json
yt-agent run --topic "Why the sky changes color" --episode-id ep-001
yt-agent qa --episode-dir runtime/episodes/ep-001/v1
yt-agent publish-prep --episode-dir runtime/episodes/ep-001/v1 --approved-by "speinnov" --publish-at "2026-10-25T18:00:00Z"
```

## Guardrails

Research is untrusted data, external assets need provenance, synthetic media requires disclosure, uploads default to private, and public release stays human-approved.
