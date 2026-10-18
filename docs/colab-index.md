# Colab index

Use **only** the canonical runner below for mobile video production:

- [Canonical Mobile Video Creator](https://colab.research.google.com/github/studio1111/YouTube-bot/blob/main/colab/yt_agent_mobile_video_creator_final.ipynb)

It is self-contained, does not clone the repository, does not use stale commits, never calls `gTTS(lang='fa')`, validates that MP4 exists and is non-empty, and falls back from Edge TTS to espeak-ng or explicitly labelled silence.

Other notebooks are retained for benchmark/history only. Do not use the old gTTS Persian notebook or the original repo-cloning creator for production.
