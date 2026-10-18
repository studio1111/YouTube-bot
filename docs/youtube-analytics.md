# YouTube Analytics integration

The Analytics adapter uses OAuth with the read-only scope `yt-analytics.readonly`, then calls `reports.query` for `impressions`, `views`, and `impressionsClickThroughRate`.

## Setup

1. Create/select a Google Cloud project.
2. Enable **YouTube Analytics API**.
3. Create OAuth client credentials for a desktop application.
4. Download the JSON file outside the repository.
5. Install the optional dependency profile:

```bash
pip install -e '.[youtube]'
```

6. Run the command. The first run opens a browser for consent and stores a local refresh token at `runtime/youtube-token.json`:

```bash
yt-agent analytics \
  --experiment-file runtime/experiments/sky-001/experiment.json \
  --credentials-file /secure/path/client_secret.json \
  --start-date 2026-10-01 \
  --end-date 2026-10-18
```

You can also set `YOUTUBE_CLIENT_SECRET_FILE` and omit `--credentials-file`.

## Important limitation

The public YouTube Analytics API does **not** expose a generic `variant` dimension that maps impressions to thumbnail/title A/B variants. The adapter accepts rows shaped like `[variant, impressions, views, ctr]` so an approved experiment proxy or exported experiment-level report can be used, but ordinary video-level Analytics data cannot honestly identify a thumbnail winner.

Do not treat aggregate video CTR as an A/B result. To make the winner calculation truthful, the experiment runner must record which variant was active during each controlled traffic window, then join that schedule with time-bucketed Analytics snapshots. The current implementation provides the OAuth client, snapshot schema, validation, and winner calculation; it intentionally refuses to invent variant attribution.

## Winner rule

Both variants need at least 100 impressions. The winner is the variant with the highest CTR. Ties remain ties. Metrics and the decision are written back into `experiment.json`.

## Security

- Never commit client secrets or refresh tokens.
- Keep the token path under ignored `runtime/`.
- Use read-only OAuth scope.
- Review and approve any future upload or title/thumbnail rotation separately.

Official references: [Reports.query](https://developers.google.com/youtube/analytics/reference/reports/query), [YouTube Analytics API](https://developers.google.com/youtube/analytics), and [Google API OAuth for installed apps](https://googleapis.github.io/google-api-python-client/docs/oauth-installed.html).
