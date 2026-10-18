# Colab and GitHub Actions benchmark bridge

## Fastest phone-only path

Open this notebook directly in Google Colab:

[**Open the mobile benchmark in Colab**](https://colab.research.google.com/github/studio1111/YouTube-bot/blob/main/colab/yt_agent_mobile_benchmark.ipynb)

On Android or iPhone:

1. Tap the link.
2. Sign in to Google if asked.
3. Open the **Runtime** menu and tap **Run all**.
4. Wait for the file `mobile-render-benchmark.json` to download.
5. Send that JSON here for comparison, or use the optional Drive backup cell.

No local computer, terminal, API key, GitHub token, YouTube OAuth, Telegram credential, or SMTP password is needed. Keep the optional Drive cell off unless you want a backup.

## What it measures

The report records mode timings, output size, FFmpeg/Python/platform details, and whether `nvidia-smi` sees a GPU. It benchmarks the repository's six render paths. The `comfyui-workflow` mode exports a workflow and measures the local fallback renderer; it does not claim Wan2.1/FLUX inference.

## More accurate results

Set `REPEATS = 3` in the second cell when you have time. The default `REPEATS = 1` is intentionally phone-friendly and faster. Compare Colab CPU, Colab T4, and GitHub Actions CPU as separate hardware classes.

## GitHub Actions

The existing GitHub Actions bridge still needs the repository's **Workflow** permission before `.github/workflows/*` can be added. Colab does not require that permission and is the easiest route from a phone.
