# Mobile video creation with Colab

[**Open Mobile Video Creator in Colab**](https://colab.research.google.com/github/studio1111/YouTube-bot/blob/main/colab/yt_agent_mobile_video_creator.ipynb)

Run **Runtime → Run all**. The default mode is now `slides`, the most compatible hosted-FFmpeg path. Change it to `ken-burns` after the first successful run. The renderer now retries with a minimal filtergraph and writes `render_error.log` when FFmpeg rejects a command. Cell 3 prints that exact error instead of giving an opaque `FileNotFoundError`.
