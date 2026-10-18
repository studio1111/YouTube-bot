# 100% Free Video Generation Modes (`video_engines.py`)

`yt-agent` supports six completely free, zero-subscription video creation pipelines selectable via `--video-mode`:

| Mode (`--video-mode`) | Aspect Ratio | How It Works (100% Free) | Best For |
|---|---|---|---|
| `ken-burns` *(default)* | 16:9 (`1280x720`) | Procedural scene synthesis + cinematic pan/crop FFmpeg filtergraph + WAV audio | Long-form explainers on CPU-only machines |
| `shorts-vertical` | 9:16 (`1080x1920`) | Vertical procedural gradients + dynamic pacing + AAC audio | YouTube Shorts, Reels, TikTok cutdowns |
| `audiogram` | 16:9 (`1280x720`) | Waveform-inspired visual bars synced with narration track | Podcast clips, voice-first stories |
| `openverse-broll` | 16:9 (`1280x720`) | Queries Openverse API for CC0 / CC-BY images + writes `broll/broll_sources.json` attribution ledger | Documentary explainers with licensed Commons visuals |
| `comfyui-workflow` | 16:9 / 9:16 | Exports ready-to-run local **ComfyUI + FLUX.1 Schnell + Wan2.1-T2V-1.3B** (Apache-2.0) JSON workflow + fallback MP4 | Local GPU AI video & image-to-video generation |
| `slides` | 16:9 (`1280x720`) | Clean deterministic storyboard frames + FFmpeg H.264 encode | Fast offline drafts & CI testing |

## Usage

```bash
# List all available free video modes
yt-agent video-modes

# 1. Cinematic 16:9 Ken Burns explainer
yt-agent run --topic "How photonic chips work" --episode-id ep-photonic --video-mode ken-burns

# 2. Vertical 9:16 YouTube Short (1080x1920)
yt-agent run --topic "Why neutron stars spin so fast" --episode-id ep-short-01 --video-mode shorts-vertical

# 3. Openverse Creative Commons B-Roll with automatic attribution ledger
yt-agent run --topic "Deep ocean hydrothermal vents" --episode-id ep-vents --video-mode openverse-broll

# 4. Local AI GPU Workflow (ComfyUI + FLUX.1 Schnell + Wan2.1 Apache-2.0)
yt-agent run --topic "Quantum tunneling visualized" --episode-id ep-quantum --video-mode comfyui-workflow
```
