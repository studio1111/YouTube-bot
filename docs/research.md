# Research notes and source map

Research completed for the initial architecture on 2026-10-18. Verify licenses and API policies again before production because they change.

## Reference projects

- [OpenMontage](https://github.com/calesthio/OpenMontage): stage contracts, checkpoints, provider selection, approvals, and QA gates. AGPL-3.0.
- [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo): practical topic-to-short pipeline, batch manifests, TTS, captions, and FFmpeg. MIT.
- [Pixelle-Video](https://github.com/ATH-MaaS/Pixelle-Video): provider adapters, ComfyUI workflows, and template-driven composition. Apache-2.0.
- [ComfyUI](https://github.com/Comfy-Org/ComfyUI): declarative generation graphs and queueing. GPL-3.0.
- [VideoLingo](https://github.com/Huanshere/VideoLingo): timed captions, terminology memory, translation, and dubbing. Apache-2.0.
- [Open-Sora](https://github.com/hpcaitech/Open-Sora): reproducible model invocation and batch generation patterns. Apache-2.0 code with separate model/checkpoint terms.

## Recommended local tools

- [Ollama](https://github.com/ollama/ollama) + [Qwen](https://github.com/QwenLM/Qwen3) for local text generation.
- [Kokoro](https://github.com/hexgrad/kokoro) or [Piper](https://github.com/rhasspy/piper) for local TTS.
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) or [whisper.cpp](https://github.com/ggml-org/whisper.cpp) for transcription.
- [FFmpeg](https://ffmpeg.org/) and [MoviePy](https://github.com/Zulko/moviepy) for rendering.
- [Openverse](https://openverse.org/about/) and Wikimedia Commons for discoverable assets, with per-asset license verification.
- [YouTube Data API](https://developers.google.com/youtube/v3) for private upload and scheduling after approval.

## Important constraints

- YouTube API use is quota-limited and requires OAuth.
- YouTube publishing should keep final user control; this project uses private upload plus a release gate.
- AI-altered realistic content may require disclosure.
- Mass-produced repetitive videos can create monetization and quality risks.
- Software licenses do not grant rights to third-party media, voices, likenesses, fonts, or music.
- “Free” means no required subscription in the default path, not zero infrastructure cost.
