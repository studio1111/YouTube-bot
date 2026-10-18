from __future__ import annotations

import json
import textwrap
from pathlib import Path

from .audio import generate_narration_wav
from .models import EpisodeManifest, EpisodeState, Source
from .qa import evaluate_episode_qa
from .seo import write_seo_package
from .subtitles import write_subtitles
from .video_engines import FREE_VIDEO_MODES, prepare_visual_assets, render_with_mode


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


def build_video(
    topic: str | None = None,
    runtime_dir: str = "runtime",
    episode_id: str = "episode-001",
    video_mode: str = "ken-burns",
) -> Path:
    if video_mode not in FREE_VIDEO_MODES:
        raise ValueError(f"Unsupported video_mode '{video_mode}'. Choose from: {', '.join(FREE_VIDEO_MODES)}")

    root = Path(runtime_dir) / "episodes" / episode_id / "v1"
    frames = root / "frames"
    frames.mkdir(parents=True, exist_ok=True)
    idea = generate_idea(topic)
    script_path = write_script(idea, root / "script.txt")
    script_text = script_path.read_text(encoding="utf-8")
    srt_path, vtt_path = write_subtitles(root, script_text)
    seo_path = write_seo_package(root, idea["title"], script_text, sources=["local://generated"])
    slides = [idea["hook"], *idea["beats"], idea["close"]]

    extra_artifacts = prepare_visual_assets(idea["title"], slides, frames, root, mode=video_mode)
    audio_wav = generate_narration_wav(script_text, root / "narration.wav", duration_sec=float(len(slides)))
    output = root / "video.mp4"
    rendered = render_with_mode(frames, audio_wav, output, mode=video_mode, fps=12)
    if not rendered:
        output = root / "video-not-rendered.txt"
        output.write_text("Install FFmpeg and rerun to create video.mp4.\n", encoding="utf-8")

    artifacts = {
        "script": "script.txt",
        "audio": audio_wav.name,
        "subtitles_srt": srt_path.name,
        "subtitles_vtt": vtt_path.name,
        "seo": seo_path.name,
        "video": output.name,
        "video_mode": video_mode,
        "frames": "frames/",
    }
    for k, v in extra_artifacts.items():
        artifacts[k] = str(v)

    manifest = EpisodeManifest(
        episode_id=episode_id,
        topic=idea["title"],
        state=EpisodeState.RENDERED if rendered else EpisodeState.ASSET_PRODUCTION,
        sources=[Source(url="local://generated", title="Deterministic local starter idea", license="project")],
        artifacts=artifacts,
    )
    (root / "manifest.json").write_text(
        json.dumps(manifest.model_dump(mode="json"), indent=2), encoding="utf-8"
    )
    evaluate_episode_qa(root)
    return output
