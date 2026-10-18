from __future__ import annotations

import json
import shutil
import subprocess
import textwrap
from pathlib import Path

from .models import EpisodeManifest, EpisodeState, Source
from .qa import evaluate_episode_qa
from .seo import write_seo_package
from .subtitles import write_subtitles


DEFAULT_IDEA = {
    "title": "Why the sky changes color",
    "hook": "The sky is not blue because of the ocean. The real reason is hiding in the air above you.",
    "beats": [
        "Sunlight looks white, but it contains many colors.",
        "Earth's atmosphere scatters short blue wavelengths more strongly.",
        "At sunset, light travels through more atmosphere, leaving warm reds and oranges.",
    ],
    "close": "Look up tonight and you are watching physics in real time.",
}


def generate_idea(topic: str | None = None) -> dict:
    """Create a deterministic starter idea; an LLM adapter can replace this later."""
    if topic:
        title = topic.strip().rstrip(".")
        return {
            "title": title,
            "hook": f"Here is the surprising story behind {title.lower()}.",
            "beats": [
                f"Start with the question: what do most people get wrong about {title.lower()}?",
                "Explain one clear mechanism with a concrete example.",
                "End with a memorable fact the viewer can repeat.",
            ],
            "close": "That is the idea in one minute.",
        }
    return DEFAULT_IDEA.copy()


def write_script(idea: dict, target: Path) -> Path:
    lines = [idea["hook"], *idea["beats"], idea["close"]]
    script = "\n\n".join(lines) + "\n"
    target.write_text(script, encoding="utf-8")
    return target


def _wrap(text: str, width: int = 34) -> list[str]:
    return textwrap.wrap(text, width=width) or [""]


def _ppm_slide(path: Path, heading: str, body: str, index: int, total: int) -> None:
    width, height = 1280, 720
    pixels = bytearray()
    for y in range(height):
        for x in range(width):
            t = y / height
            pixels.extend((int(10 + 18 * t), int(20 + 25 * t), int(48 + 45 * t)))
    for y in range(48, 62):
        for x in range(70, width - 70):
            pos = (x - 70) / (width - 140)
            pixels[y * width * 3 + x * 3 : y * width * 3 + x * 3 + 3] = bytes(
                (52, int(180 - 80 * pos), 220)
            )
    path.write_bytes(f"P6\n{width} {height}\n255\n".encode() + pixels)


def _run_ffmpeg(frames: Path, output: Path, fps: int, title: str) -> bool:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return False
    output.parent.mkdir(parents=True, exist_ok=True)
    pattern = str(frames / "slide-%03d.ppm")
    vf = (
        "drawtext=text='" + title.replace("'", "\\'") + "':"
        "fontcolor=white:fontsize=42:x=70:y=100,"
        "drawtext=text='Vertical slice':fontcolor=0x9bdcff:fontsize=24:x=70:y=650"
    )
    proc = subprocess.run(
        [ffmpeg, "-y", "-framerate", str(fps), "-i", pattern, "-vf", vf,
         "-c:v", "libx264", "-pix_fmt", "yuv420p", str(output)],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        proc2 = subprocess.run(
            [ffmpeg, "-y", "-framerate", str(fps), "-i", pattern,
             "-c:v", "libx264", "-pix_fmt", "yuv420p", str(output)],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        return proc2.returncode == 0
    return True


def build_video(topic: str | None = None, runtime_dir: str = "runtime", episode_id: str = "episode-001") -> Path:
    root = Path(runtime_dir) / "episodes" / episode_id / "v1"
    frames = root / "frames"
    frames.mkdir(parents=True, exist_ok=True)
    idea = generate_idea(topic)
    script_path = write_script(idea, root / "script.txt")
    script_text = script_path.read_text(encoding="utf-8")
    srt_path, vtt_path = write_subtitles(root, script_text)
    seo_path = write_seo_package(root, idea["title"], script_text, sources=["local://generated"])
    slides = [idea["hook"], *idea["beats"], idea["close"]]
    for i, text in enumerate(slides, 1):
        _ppm_slide(frames / f"slide-{i:03d}.ppm", idea["title"], text, i, len(slides))
    output = root / "video.mp4"
    rendered = _run_ffmpeg(frames, output, fps=1, title=idea["title"])
    if not rendered:
        output = root / "video-not-rendered.txt"
        output.write_text("Install FFmpeg and rerun to create video.mp4.\n", encoding="utf-8")
    manifest = EpisodeManifest(
        episode_id=episode_id,
        topic=idea["title"],
        state=EpisodeState.RENDERED if rendered else EpisodeState.ASSET_PRODUCTION,
        sources=[Source(url="local://generated", title="Deterministic local starter idea", license="project")],
        artifacts={
            "script": "script.txt",
            "subtitles_srt": srt_path.name,
            "subtitles_vtt": vtt_path.name,
            "seo": seo_path.name,
            "video": output.name,
            "frames": "frames/",
        },
    )
    (root / "manifest.json").write_text(
        json.dumps(manifest.model_dump(mode="json"), indent=2), encoding="utf-8"
    )
    evaluate_episode_qa(root)
    return output
