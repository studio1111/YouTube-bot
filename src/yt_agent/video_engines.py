from __future__ import annotations

import json
import math
import shutil
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


FREE_VIDEO_MODES = (
    "ken-burns",
    "shorts-vertical",
    "audiogram",
    "openverse-broll",
    "comfyui-workflow",
    "slides",
)


def _write_procedural_ppm(path: Path, width: int, height: int, scene_idx: int, mode: str) -> Path:
    """Create a rich procedural visual frame with zero external dependencies."""
    path.parent.mkdir(parents=True, exist_ok=True)
    pixels = bytearray()
    phase = scene_idx * 0.85
    for y in range(height):
        ny = y / max(1, height)
        for x in range(width):
            nx = x / max(1, width)
            wave = 0.5 + 0.5 * math.sin(6.0 * nx + 4.0 * ny + phase)
            if mode == "shorts-vertical":
                r = int(16 + 55 * ny + 35 * wave)
                g = int(22 + 95 * (1 - nx) + 40 * wave)
                b = int(68 + 135 * wave)
            elif mode == "audiogram":
                bar = 1.0 if abs(ny - 0.5) < (0.08 + 0.14 * abs(math.sin(18 * nx + phase))) else 0.15
                r = int(14 + 140 * bar)
                g = int(28 + 195 * bar)
                b = int(42 + 90 * bar)
            else:
                r = int(12 + 38 * ny + 44 * wave)
                g = int(26 + 70 * nx + 55 * wave)
                b = int(58 + 120 * (1 - ny) + 50 * wave)
            pixels.extend((min(255, r), min(255, g), min(255, b)))
    path.write_bytes(f"P6\n{width} {height}\n255\n".encode("ascii") + bytes(pixels))
    return path


def fetch_openverse_Commons(query: str, out_dir: Path, limit: int = 3) -> list[dict[str, str]]:
    """Query the free Openverse API for Creative Commons (CC0 / CC-BY) images with full attribution."""
    out_dir.mkdir(parents=True, exist_ok=True)
    params = urllib.parse.urlencode(
        {"q": query, "license": "cc0,by", "page_size": str(limit)}
    )
    url = f"https://api.openverse.org/v1/images/?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "yt-agent-free-video/0.1"})
    records: list[dict[str, str]] = []
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        for item in payload.get("results", [])[:limit]:
            records.append(
                {
                    "title": item.get("title") or query,
                    "url": item.get("foreign_landing_url") or item.get("url") or "https://openverse.org",
                    "creator": item.get("creator") or "Openverse Contributor",
                    "license": f"CC-{str(item.get('license', 'by')).upper()}",
                    "attribution": item.get("attribution") or "Via Openverse Creative Commons",
                }
            )
    except Exception:
        pass
    if not records:
        records.append(
            {
                "title": f"Procedural CC0 Canvas for {query}",
                "url": "local://procedural-cc0",
                "creator": "yt-agent procedural synthesizer",
                "license": "CC0-1.0",
                "attribution": "Generated locally by yt-agent (Public Domain / CC0)",
            }
        )
    (out_dir / "broll_sources.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    return records


def export_comfyui_workflow(
    topic: str,
    beats: list[str],
    out_dir: Path,
    model_family: str = "flux1-schnell-wan2.1",
) -> Path:
    """Export a ready-to-run local ComfyUI / Wan2.1 / FLUX.1 Schnell workflow JSON for zero-cost GPU generation."""
    out_dir.mkdir(parents=True, exist_ok=True)
    workflow: dict[str, Any] = {
        "engine": "ComfyUI Local Free Workflow",
        "model_family": model_family,
        "license_note": "FLUX.1 Schnell and Wan2.1-T2V-1.3B are Apache-2.0 open-weight models.",
        "topic": topic,
        "scenes": [
            {
                "scene_index": idx,
                "prompt": f"Cinematic science explainer visual, high detail, {topic}: {beat}",
                "negative_prompt": "watermark, text overlay, blurry, low quality, distorted",
                "width": 1280,
                "height": 720,
                "frames": 81,
                "fps": 16,
                "seed": 1000 + idx,
            }
            for idx, beat in enumerate(beats, 1)
        ],
    }
    wf_path = out_dir / "comfyui_workflow.json"
    wf_path.write_text(json.dumps(workflow, indent=2), encoding="utf-8")
    return wf_path


def render_with_mode(
    frames_dir: Path,
    audio_wav: Path,
    output_mp4: Path,
    mode: str = "ken-burns",
    fps: int = 24,
) -> bool:
    """Render MP4 using free FFmpeg filtergraphs tailored to each production mode."""
    if mode not in FREE_VIDEO_MODES:
        raise ValueError(f"Unsupported video mode '{mode}'. Choose from: {', '.join(FREE_VIDEO_MODES)}")

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return False

    output_mp4.parent.mkdir(parents=True, exist_ok=True)
    pattern = str(frames_dir / "slide-%03d.ppm")

    if mode == "shorts-vertical":
        vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=yuv420p"
    elif mode == "ken-burns":
        vf = "scale=1408:792,crop=1280:720:x='(in_w-out_w)/2':y='(in_h-out_h)/2',format=yuv420p"
    elif mode == "audiogram":
        vf = "scale=1280:720,eq=contrast=1.08:saturation=1.18,format=yuv420p"
    else:
        vf = "scale=1280:720,format=yuv420p"

    cmd = [
        ffmpeg,
        "-y",
        "-framerate",
        "1",
        "-i",
        pattern,
        "-i",
        str(audio_wav),
        "-vf",
        vf,
        "-r",
        str(fps),
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-shortest",
        "-pix_fmt",
        "yuv420p",
        str(output_mp4),
    ]
    proc = subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    return proc.returncode == 0


def prepare_visual_assets(
    topic: str,
    slides: list[str],
    frames_dir: Path,
    episode_root: Path,
    mode: str = "ken-burns",
) -> dict[str, Any]:
    """Generate procedural frames plus mode-specific free assets (Openverse CC metadata or ComfyUI workflow)."""
    if mode not in FREE_VIDEO_MODES:
        raise ValueError(f"Unsupported video mode '{mode}'. Choose from: {', '.join(FREE_VIDEO_MODES)}")

    width, height = (180, 320) if mode == "shorts-vertical" else (320, 180)
    for idx, _ in enumerate(slides, 1):
        _write_procedural_ppm(frames_dir / f"slide-{idx:03d}.ppm", width, height, idx, mode)

    extras: dict[str, Any] = {"video_mode": mode}
    if mode == "openverse-broll":
        records = fetch_openverse_Commons(topic, episode_root / "broll")
        extras["broll_sources"] = "broll/broll_sources.json"
        extras["openverse_count"] = len(records)
    elif mode == "comfyui-workflow":
        wf = export_comfyui_workflow(topic, slides, episode_root / "workflows")
        extras["comfyui_workflow"] = str(wf.relative_to(episode_root))
    return extras
