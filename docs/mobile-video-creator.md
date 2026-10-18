# Mobile video creation with Colab

## One-tap path

Open the notebook:

[**Open Mobile Video Creator in Colab**](https://colab.research.google.com/github/studio1111/YouTube-bot/blob/main/colab/yt_agent_mobile_video_creator.ipynb)

Then:

1. Tap **Runtime → Run all**.
2. In cell 2, change `TOPIC`, `EPISODE_ID`, and `VIDEO_MODE` if needed.
3. Wait for rendering.
4. Cell 3 downloads a ZIP package to the phone.

## Recommended modes

- `ken-burns`: safest default for a 16:9 explainer.
- `shorts-vertical`: 9:16 mobile-first output.
- `audiogram`: fastest voice-led format.
- `slides`: most predictable offline draft.
- `openverse-broll`: adds public Creative Commons source metadata; network access may be slow.
- `comfyui-workflow`: exports a local GPU workflow and renders the fallback in this simple notebook; it does not claim that model inference completed.

The notebook does not upload or publish to YouTube. Review the MP4 and run the separate approval-gated upload flow only after the result is acceptable.
