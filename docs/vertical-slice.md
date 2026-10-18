# Vertical slice: idea to local video

This is the first executable path through the product. It deliberately uses deterministic local generation so it works without API keys or paid services.

## Flow

```text
optional topic
  -> deterministic idea brief
  -> plain-text script
  -> PPM slide frames
  -> FFmpeg MP4 with title overlays
  -> manifest with state and artifacts
```

## Run

```bash
pip install -e '.[dev]'
# Install ffmpeg separately if you want video.mp4 instead of a reminder file.
yt-agent run --topic 'Why electric cars are quiet' --episode-id ep-001
```

Output is under `runtime/episodes/<episode-id>/v1/`. It contains `script.txt`, five frame images, `video.mp4` when FFmpeg is available, and `manifest.json`.

## Why this shape

- No network, API key, model download, or cloud account is required.
- The output contract is already compatible with future Ollama, TTS, image, caption, and YouTube adapters.
- FFmpeg receives a fixed command assembled by trusted code; generated text never becomes shell syntax.
- The next upgrade should replace `generate_idea` and `write_script` behind provider interfaces, then add narration and captions.

## Known limitations

This is a production-shaped skeleton, not a polished editor: no narration, stock media, semantic research, subtitles, thumbnail, or upload yet. The deliberately boring first slice is useful because it tests artifact versioning, rendering, and manifest contracts before GPU or API complexity arrives.
