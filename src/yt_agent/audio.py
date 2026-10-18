from __future__ import annotations

import math
import shutil
import struct
import subprocess
import wave
from pathlib import Path


def _synthesize_ambient_wav(path: Path, duration_sec: float = 5.0, sample_rate: int = 22050) -> Path:
    """Generate a clean, royalty-free ambient chime/pad WAV using only the Python standard library."""
    path.parent.mkdir(parents=True, exist_ok=True)
    total_samples = max(1, int(duration_sec * sample_rate))
    with wave.open(str(path), "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        frames = bytearray()
        for i in range(total_samples):
            t = i / sample_rate
            fade_in = min(1.0, t / 0.4)
            fade_out = min(1.0, max(0.0, (duration_sec - t) / 0.6))
            env = fade_in * fade_out * 0.22
            sample = env * (0.65 * math.sin(2 * math.pi * 220.0 * t) + 0.35 * math.sin(2 * math.pi * 329.63 * t))
            val = max(-32767, min(32767, int(sample * 32767)))
            frames.extend(struct.pack("<h", val))
        wav.writeframes(bytes(frames))
    return path


def generate_narration_wav(
    script_text: str,
    target_wav: str | Path,
    duration_sec: float = 5.0,
) -> Path:
    """Create narration audio via local espeak-ng/piper if installed, or fall back to a royalty-free ambient WAV."""
    out = Path(target_wav)
    out.parent.mkdir(parents=True, exist_ok=True)
    espeak = shutil.which("espeak-ng") or shutil.which("espeak")
    if espeak:
        proc = subprocess.run(
            [espeak, "-w", str(out), script_text[:1500]],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        if proc.returncode == 0 and out.exists() and out.stat().st_size > 44:
            return out
    return _synthesize_ambient_wav(out, duration_sec=duration_sec)
