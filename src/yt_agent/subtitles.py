from __future__ import annotations

from pathlib import Path


def _srt_time(seconds: float) -> str:
    millis = int(round(max(0.0, seconds) * 1000))
    hrs, rem = divmod(millis, 3_600_000)
    mins, rem = divmod(rem, 60_000)
    secs, ms = divmod(rem, 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{ms:03d}"


def _vtt_time(seconds: float) -> str:
    return _srt_time(seconds).replace(",", ".")


def segment_script(script_text: str, seconds_per_segment: float = 4.0) -> list[dict[str, float | str]]:
    lines = [p.strip() for p in script_text.split("\n\n") if p.strip()]
    segments: list[dict[str, float | str]] = []
    cursor = 0.0
    for line in lines:
        duration = max(2.5, min(8.0, len(line.split()) * 0.42)) if seconds_per_segment <= 0 else seconds_per_segment
        segments.append({"start": round(cursor, 2), "end": round(cursor + duration, 2), "text": line})
        cursor += duration
    return segments


def render_srt(segments: list[dict[str, float | str]]) -> str:
    blocks = []
    for idx, seg in enumerate(segments, 1):
        blocks.append(
            f"{idx}\n{_srt_time(float(seg['start']))} --> {_srt_time(float(seg['end']))}\n{seg['text']}"
        )
    return "\n\n".join(blocks) + ("\n" if blocks else "")


def render_vtt(segments: list[dict[str, float | str]]) -> str:
    blocks = ["WEBVTT"]
    for seg in segments:
        blocks.append(f"{_vtt_time(float(seg['start']))} --> {_vtt_time(float(seg['end']))}\n{seg['text']}")
    return "\n\n".join(blocks) + "\n"


def write_subtitles(episode_dir: str | Path, script_text: str, seconds_per_segment: float = 4.0) -> tuple[Path, Path]:
    root = Path(episode_dir)
    root.mkdir(parents=True, exist_ok=True)
    segments = segment_script(script_text, seconds_per_segment=seconds_per_segment)
    srt_path = root / "captions.srt"
    vtt_path = root / "captions.vtt"
    srt_path.write_text(render_srt(segments), encoding="utf-8")
    vtt_path.write_text(render_vtt(segments), encoding="utf-8")
    return srt_path, vtt_path
