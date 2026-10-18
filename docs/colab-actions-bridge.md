# Colab and GitHub Actions benchmark bridge

`colab/yt_agent_hardware_benchmark.ipynb` runs the same portable benchmark on a temporary Colab CPU/GPU runtime. `scripts/benchmark.py` writes the `yt-agent.render-benchmark.v1` JSON schema with mode timings, output size, FFmpeg/Python/platform details, and GPU detection.

## Colab

1. Open the notebook in Colab.
2. Choose Runtime → Change runtime type → T4 GPU if available.
3. Run all cells and download `render-benchmark.json`.
4. Review it, then commit it as `runtime/benchmarks/colab-YYYYMMDD.json` or attach it to a GitHub Issue.

The current `comfyui-workflow` mode exports a workflow and measures the local fallback renderer; it does not claim actual Wan2.1/FLUX inference. A true model benchmark must record checkpoint hash, VRAM, resolution, frame count, seed, and inference time separately.

## GitHub Actions

The workflow file cannot be added with the current GitHub connection because creating `.github/workflows/*` requires the repository's **Workflow** permission. Once that scope is enabled, add a workflow that runs `python scripts/benchmark.py` on `ubuntu-latest`, uploads `render-benchmark.json` with `actions/upload-artifact@v4`, and keeps it explicitly labeled CPU-only.

## Safe comparison

Only compare reports with the same topic, script, narration, scene count, FFmpeg version, resolution, frame rate, repeats, and mode. Label reports `colab-cpu`, `colab-t4`, or `github-actions-ubuntu-cpu`; never merge hardware results into one average.

Never commit YouTube OAuth files, Telegram tokens, SMTP passwords, or notebook outputs containing secrets.
