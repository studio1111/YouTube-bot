# Project map

- `src/yt_agent/idea_intelligence.py`: authorized multi-platform idea collection, dedupe, ranking, and hook patterns.
- `src/yt_agent/scenario_prompts.py`: structured original scenario generation with local Ollama fallback.
- `src/yt_agent/video_engines.py`: six free render modes and rights-aware visual asset preparation.
- `src/yt_agent/vertical_slice.py`: script → audio → captions → SEO → visuals → MP4 → QA.
- `src/yt_agent/qa.py`: factual/provenance/caption/metadata/disclosure gate.
- `src/yt_agent/provenance.py`: SHA-256 artifact ledger.
- `src/yt_agent/publisher.py`: private/unlisted package preparation.
- `src/yt_agent/youtube_publish.py`: resumable OAuth upload to private/unlisted.
- `src/yt_agent/release.py`: final package validation.
- `src/yt_agent/analytics.py`: read-only Analytics and incomplete-data warnings.
- `src/yt_agent/notifications.py`: Telegram and SMTP alert delivery.
- `src/yt_agent/runtime.py`: SQLite idempotency/run ledger.
- `src/yt_agent/dashboard.py`: local static control room.
- `colab/`: phone-first pinned execution and hardware benchmark notebooks.
- `docs/`: research, policy, operations, security, release, and monetization runbooks.
