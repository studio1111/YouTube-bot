# Mobile video creation with Colab

## One-tap option

[**Open the one-tap mobile video builder in Colab**](https://colab.research.google.com/github/studio1111/YouTube-bot/blob/main/colab/yt_agent_mobile_video_creator_one_tap.ipynb)

1. Open the link on Android or iPhone.
2. Change `TOPIC` only if you want.
3. Tap **Runtime → Run all**.
4. Wait for the ZIP download.

It checks out tested commit `63a4d57d4a90a50707044447fe810cbaec4f2f41`, installs FFmpeg if needed, renders the selected mode, and downloads MP4 plus script, narration, captions, SEO, QA, and manifest files. `slides` is the safest default; use `shorts-vertical` for a 9:16 Short.

No computer, terminal, API key, GitHub token, YouTube OAuth, Telegram credential, or SMTP password is needed. Publishing is not automatic: review the ZIP first.
