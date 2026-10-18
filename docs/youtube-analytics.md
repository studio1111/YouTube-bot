# YouTube Analytics integration

The Analytics adapter uses OAuth with the read-only scope `yt-analytics.readonly`, then calls `reports.query` for `impressions`, `views`, and `impressionsClickThroughRate`.

## Setup

```bash
pip install -e '.[youtube]'
yt-agent analytics --experiment-file runtime/experiments/sky-001/experiment.json --credentials-file /secure/path/client_secret.json --start-date 2026-10-01 --end-date 2026-10-18
```

The first run opens browser consent and stores a local refresh token at `runtime/youtube-token.json`. Keep credentials and tokens out of Git.

## Automatic incomplete-data warnings

Every Analytics result now includes `analytics.warnings`. The system warns when:

- one or more expected variant rows are missing;
- fewer than two usable rows are returned;
- a variant is below the 100-impression minimum;
- metric values are malformed or outside valid ranges;
- the top variants tie on CTR.

Any incomplete or invalid result stays `insufficient_data` and cannot select a winner. Warnings are persisted in `experiment.json` so a scheduler, UI, or notification worker can alert on `analytics.warnings` without re-running the query.

## Important limitation

The public YouTube Analytics API does **not** expose a generic `variant` dimension that maps impressions to thumbnail/title A/B variants. The adapter accepts rows shaped like `[variant, impressions, views, ctr]` so an approved experiment proxy or exported experiment-level report can be used, but ordinary video-level Analytics data cannot honestly identify a thumbnail winner.

Do not treat aggregate video CTR as an A/B result. The experiment runner must record which variant was active during each controlled traffic window, then join that schedule with time-bucketed Analytics snapshots.
