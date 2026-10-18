# Free video engine benchmark

## Verdict

For CPU-first production, **audiogram** is fastest and smallest, **ken-burns** is the best general long-form default, and **shorts-vertical** is the most expensive render because it produces 1080x1920 output. `openverse-broll` is not CPU-expensive; its measured delay came from the external asset lookup and should be treated as network-variable.

## Measured sample

Benchmark input: four procedural scenes, one local WAV narration, 10 fps encode setting, H.264 video + AAC audio, FFmpeg available. The output duration was approximately 3.9 seconds per mode. Measurements were taken on the local development sandbox on 2026-10-18, so use them for relative comparison, not capacity planning.

| Mode | Aspect ratio | Asset prep | Render | Total | Output | Result |
|---|---:|---:|---:|---:|---:|---|
| `audiogram` | 16:9 | 0.345 s | **0.364 s** | **0.709 s** | 67.9 KB | Pass |
| `slides` | 16:9 | 0.342 s | 0.470 s | 0.813 s | 165.2 KB | Pass |
| `ken-burns` | 16:9 | 0.351 s | 0.504 s | 0.854 s | 161.8 KB | Pass |
| `comfyui-workflow` | 16:9 fallback | 0.372 s | 0.530 s | 0.903 s | 165.2 KB | Pass, workflow exported |
| `shorts-vertical` | 9:16 | 0.327 s | **0.825 s** | **1.152 s** | 291.0 KB | Pass |
| `openverse-broll` | 16:9 | **20.439 s** | 0.516 s | **20.955 s** | 165.2 KB | Pass, one fallback/source record |

The benchmark confirms the output dimensions with `ffprobe`: landscape modes rendered 1280x720, Shorts rendered 1080x1920, and every mode included H.264 video plus AAC audio.

## What the numbers mean

- **Audiogram:** best for narration-led explainers, interviews, and podcasts when speed matters more than visual richness.
- **Slides:** best for CI fixtures, drafts, and low-risk explainers. It is predictable and easy to reproduce.
- **Ken Burns:** best default for a polished long-form draft on CPU. It gives movement without model downloads or GPU requirements.
- **ComfyUI workflow:** the benchmark measures the fallback MP4, not actual FLUX/Wan2.1 inference. Real GPU generation time depends heavily on model, VRAM, resolution, frame count, and number of shots. Do not use 0.903 seconds as an AI-generation estimate.
- **Shorts vertical:** use only when the target is actually mobile-first. The larger pixel canvas costs more, but the output is correctly 1080x1920.
- **Openverse B-roll:** the 20.439 seconds is primarily the API/network lookup. Cache source results and keep the attribution ledger; if the network fails, the code falls back to a local CC0 procedural record.

## Recommended routing policy

```text
voice-first / interview        -> audiogram
fast draft / CI                -> slides
CPU long-form explainer        -> ken-burns
real-world documentary assets  -> openverse-broll
mobile-first vertical           -> shorts-vertical
GPU + visual story payoff       -> comfyui-workflow
```

## Reproduce the comparison

```bash
# Run each mode and compare elapsed time, dimensions, and file size.
for mode in ken-burns shorts-vertical audiogram openverse-broll comfyui-workflow slides; do
  time yt-agent run \
    --topic "Quantum batteries" \
    --episode-id "benchmark-$mode" \
    --video-mode "$mode"
done

ffprobe -v error -show_entries format=duration:stream=width,height,codec_name -of json \
  runtime/episodes/benchmark-ken-burns/v1/video.mp4
```

For a fair production benchmark, use the same topic, script, narration, scene count, FFmpeg build, resolution, and hardware. Run each mode at least three times and report median and p95, especially for network-backed Openverse and GPU-backed ComfyUI.

## Limitation

This is a **render-path benchmark**, not a quality benchmark. It does not score factual quality, visual appeal, retention, or licensing suitability. Those belong to the QA report and Analytics loop. The ComfyUI path currently exports a workflow and renders the local fallback; it does not silently claim that a GPU model completed inference.
