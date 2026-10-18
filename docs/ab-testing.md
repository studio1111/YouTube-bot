# Title and thumbnail A/B experiment

Create two deterministic variants without APIs or paid design tools:

```bash
yt-agent ab-test --topic 'Why the sky changes color' --experiment-id sky-001
```

The output is `runtime/experiments/sky-001/experiment.json` plus `thumbnail-A.svg` and `thumbnail-B.svg`.

## Experiment rule

Use the same video, audience, traffic source, and publication window. Compare click-through rate after each variant has at least 100 impressions. Record impressions, clicks, CTR, and the winner in `experiment.json`; do not declare a winner from a tiny sample.

The current slice only generates assets and a measurement contract. YouTube thumbnail/title rotation and analytics ingestion are intentionally not automated yet because they require OAuth, quota handling, and a human-approved publishing workflow.
