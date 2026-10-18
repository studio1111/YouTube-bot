# Mobile video creation with Colab

## Canonical path

Use only this runner for mobile video production:

[**Open Canonical Mobile Video Creator in Colab**](https://colab.research.google.com/github/studio1111/YouTube-bot/blob/main/colab/yt_agent_mobile_video_creator_final.ipynb)

1. Open the link on Android or iPhone.
2. Set `TOPIC`, `LANGUAGE`, and `VERTICAL` in the first cell.
3. Tap **Runtime → Run all**.
4. Wait for the `SUCCESS` line and ZIP download.

The canonical notebook is self-contained and does not clone GitHub or rely on relative repository paths. It creates visible animated frames, MP4, script, captions, manifest, and audio. Persian voice uses Edge TTS first, then local `espeak-ng`, then an explicitly labelled silent fallback. It never calls `gTTS(lang='fa')`.

The older notebooks are retained for benchmark/history only. Do not use them for production.
