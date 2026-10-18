# YouTube Channel Agent

A local-first, open-source automation system for running a YouTube channel: research, ideas, scripts, SEO metadata, voice, visuals, editing, thumbnails, QA, and YouTube upload preparation.

## Working vertical slice

The first end-to-end path now works locally:

```bash
pip install -e '.[dev]'
# Install FFmpeg to render MP4. Without it, the pipeline still writes all source artifacts.
yt-agent run --topic 'Why the sky changes color' --episode-id ep-001
```

It creates an idea brief, script, five deterministic frames, an MP4 with FFmpeg when available, and a provenance manifest in `runtime/episodes/ep-001/v1/`. No network, API key, or YouTube upload is used.

> **Reality check:** fully free software does not mean zero cost. Local inference still needs hardware, electricity, storage, and model downloads. Publishing remains human-approved by design.

## Planned free/local stack

| Capability | Default | Fallback |
|---|---|---|
| Orchestration | Python state machine + SQLite | Temporal OSS |
| Local LLM | Ollama + Qwen | Any OpenAI-compatible endpoint |
| Research | RSS, YouTube Data API, SearXNG | Curated URLs |
| Speech-to-text | faster-whisper | whisper.cpp |
| Text-to-speech | Kokoro | Piper |
| Images | ComfyUI + FLUX Schnell | User-provided/Openverse assets |
| Video | FFmpeg + MoviePy | Remotion where licensing fits |
| Captions | Whisper timestamps + ASS/VTT | Manual corrections |
| Thumbnails | Pillow/SVG templates | ComfyUI image generation |
| Publishing | YouTube Data API | Export package for manual upload |

## Guardrails

Research material is untrusted data, every factual claim needs a source, external assets need provenance, uploads default to private, and public release requires explicit approval. No automated engagement manipulation and no arbitrary shell commands from an LLM.

See `docs/vertical-slice.md` for the current executable flow, `ARCHITECTURE.md` for the target system, and `docs/research.md` for source and license notes.
