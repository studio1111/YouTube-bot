# Final release runbook

## First install

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

Install FFmpeg separately for MP4 rendering. Optional YouTube OAuth dependencies are installed with `pip install -e '.[youtube]'`.

## Build one episode

```bash
yt-agent ideas --niche "quantum physics"
yt-agent scenario --idea-file runtime/ideas/idea-report-quantum-physics.json
yt-agent run --topic "Why the sky changes color" --episode-id ep-001 --video-mode slides
yt-agent provenance --episode-dir runtime/episodes/ep-001/v1
yt-agent qa --episode-dir runtime/episodes/ep-001/v1
yt-agent publish-prep --episode-dir runtime/episodes/ep-001/v1 --approved-by speinnov --publish-at 2026-10-25T18:00:00Z
yt-agent release-check --episode-dir runtime/episodes/ep-001/v1
```

`release-check` must report `ready: true` before private upload. The upload worker accepts only `private` or `unlisted`; final public release remains a human action in YouTube Studio.

## Mobile path

Use the pinned Colab notebook in `colab/yt_agent_mobile_video_creator.ipynb`. It checks out commit `63a4d57d4a90a50707044447fe810cbaec4f2f41`, uses `slides` by default, and downloads a ZIP package.

## Release blockers

- Missing source or license evidence.
- Failed QA or unresolved warnings.
- Missing provenance ledger.
- Missing explicit synthetic-media decision.
- Missing human approval.
- Missing MP4 or private upload result.
- Public publishing requested outside YouTube Studio.

## What is intentionally not automated

No scraping of private or unauthorized social accounts, no engagement manipulation, no invented analytics, no silent public upload, and no credential storage in the repository.
