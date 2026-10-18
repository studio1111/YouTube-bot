from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from yt_agent.audio import generate_narration_wav
from yt_agent.video_engines import FREE_VIDEO_MODES, prepare_visual_assets, render_with_mode


def _command_output(command: list[str]) -> str:
    try:
        return subprocess.check_output(command, text=True, stderr=subprocess.STDOUT, timeout=10).strip()
    except Exception:
        return "unavailable"


def _median(values: list[float]) -> float:
    values = sorted(values)
    middle = len(values) // 2
    if len(values) % 2:
        return round(values[middle], 4)
    return round((values[middle - 1] + values[middle]) / 2, 4)


def run_benchmark(topic: str, output_file: str, repeats: int = 3) -> Path:
    results: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="yt-agent-benchmark-") as tmp:
        root = Path(tmp)
        audio = generate_narration_wav("A short benchmark narration.", root / "narration.wav", duration_sec=4.0)
        for mode in FREE_VIDEO_MODES:
            samples: list[dict[str, float | int | bool]] = []
            for repeat in range(max(1, repeats)):
                episode = root / f"{mode}-{repeat}"
                frames = episode / "frames"
                slides = ["Hook", "Mechanism", "Example", "Close"]
                started = time.perf_counter()
                extras = prepare_visual_assets(topic, slides, frames, episode, mode=mode)
                asset_seconds = time.perf_counter() - started
                output = episode / "video.mp4"
                render_started = time.perf_counter()
                ok = render_with_mode(frames, audio, output, mode=mode, fps=10)
                render_seconds = time.perf_counter() - render_started
                samples.append({"repeat": repeat + 1, "asset_seconds": round(asset_seconds, 4), "render_seconds": round(render_seconds, 4), "total_seconds": round(asset_seconds + render_seconds, 4), "output_bytes": output.stat().st_size if output.exists() else 0, "ok": ok, "extras": extras})
            results.append({"mode": mode, "samples": samples, "median_total_seconds": _median([float(x["total_seconds"]) for x in samples]), "median_render_seconds": _median([float(x["render_seconds"]) for x in samples])})
    report = {"schema": "yt-agent.render-benchmark.v1", "generated_at": datetime.now(timezone.utc).isoformat(), "topic": topic, "repeats": repeats, "machine": {"platform": platform.platform(), "python": sys.version, "ffmpeg": _command_output(["ffmpeg", "-version"]).splitlines()[0] if shutil.which("ffmpeg") else "unavailable", "ffprobe": bool(shutil.which("ffprobe")), "nvidia_smi": _command_output(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"]) if shutil.which("nvidia-smi") else "unavailable"}, "results": results}
    path = Path(output_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", default="Quantum batteries")
    parser.add_argument("--output", default="runtime/benchmarks/render-benchmark.json")
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    print(run_benchmark(args.topic, args.output, args.repeats))
