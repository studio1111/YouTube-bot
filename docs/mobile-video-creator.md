# Mobile video creation with Colab

## Guaranteed-clean standalone path

[**Open Standalone Mobile Video Creator in Colab**](https://colab.research.google.com/github/studio1111/YouTube-bot/blob/main/colab/yt_agent_mobile_video_creator_standalone.ipynb)

This path deliberately does **not** clone the repository, install the package, or use relative paths. It creates the frames, WAV, MP4, script, and manifest directly in `/content/<episode-id>`, then downloads a ZIP.

1. Open the link on your phone.
2. Tap **Runtime → Run all**.
3. Change `TOPIC` or set `VERTICAL = True` for a portrait video.
4. Wait for `SUCCESS: ... video.mp4` and the ZIP download.

If this standalone notebook fails, the output cell will show the actual FFmpeg error; there is no hidden `video-not-rendered.txt` path or stale repository checkout involved. This is the reliable fallback while the full repo pipeline remains available separately.
