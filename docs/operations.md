# Operations and control room

The platform now has a small reliability layer that stays free and local-first.

## Run ledger

`RunLedger` stores workflow status, input hashes, outputs, and errors in SQLite. A succeeded run with the same input hash is skipped, which prevents duplicate expensive work.

## Retry policy

`with_retry` provides bounded exponential backoff with jitter for transient network/provider failures. Keep attempts low and make external side effects idempotent before retrying.

## Cost ledger

`CostLedger` records provider/stage cost events in JSONL. Local software is free, but GPU time, electricity, hosted APIs, storage, and media rights are not magically free. Use the ledger to see the real cost per episode.

## Schedule

`scheduler.py` stores queued UTC entries and returns due work. For production, invoke it from cron or a system service. It does not publish automatically.

## Dashboard

Generate a static local control-room page:

```bash
python -c 'from yt_agent.dashboard import build_dashboard; print(build_dashboard())'
```

It shows recent runs and tracked cost without exposing credentials or requiring a web server.

## Incident response

1. Stop public release and leave the upload private.
2. Open the run ledger and QA report.
3. Check the related GitHub Issue and Notification Nudge Nolan report.
4. Fix the smallest failing stage and rerun with a new version.
5. Record the outcome; never overwrite the approved artifact.
