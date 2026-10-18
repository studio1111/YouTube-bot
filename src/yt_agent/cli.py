import argparse
import json
from pathlib import Path

from .ab_test import create_experiment
from .analytics import YouTubeAnalyticsClient, date_window, snapshot_experiment
from .autopilot import run_autopilot
from .branding import build_brand_kit
from .notifications import send_alerts
from .pipeline import EpisodePipeline
from .publisher import prepare_publish_package
from .qa import evaluate_episode_qa
from .seo import write_seo_package
from .subtitles import write_subtitles
from .trends import discover_trends
from .vertical_slice import build_video
from .video_engines import FREE_VIDEO_MODES


def main() -> None:
    parser = argparse.ArgumentParser(description="Autonomous local-first YouTube channel agent")
    sub = parser.add_subparsers(dest="command", required=True)

    auto = sub.add_parser("autopilot", help="run complete pipeline: trends -> branding -> video -> A/B -> QA -> publish prep")
    auto.add_argument("--niche", required=True)
    auto.add_argument("--channel-name", default="Deep Cosmos")
    auto.add_argument("--episode-id", default="ep-auto-001")
    auto.add_argument("--runtime-dir", default="runtime")
    auto.add_argument("--approved-by")
    auto.add_argument("--publish-at")

    demo = sub.add_parser("demo", help="create a local episode manifest")
    demo.add_argument("--topic", required=True)
    demo.add_argument("--episode-id", default="episode-001")

    run = sub.add_parser("run", help="generate script, audio, subtitles, SEO, visuals, QA, and MP4")
    run.add_argument("--topic")
    run.add_argument("--episode-id", default="episode-001")
    run.add_argument("--runtime-dir", default="runtime")
    run.add_argument("--video-mode", choices=list(FREE_VIDEO_MODES), default="ken-burns")

    modes = sub.add_parser("video-modes", help="list all 100% free video generation modes")

    trends = sub.add_parser("trends", help="discover and score video ideas for a niche")
    trends.add_argument("--niche", required=True)
    trends.add_argument("--runtime-dir", default="runtime")
    trends.add_argument("--searxng-url")
    trends.add_argument("--feeds", nargs="*")

    brand = sub.add_parser("branding", help="generate SVG channel logo, banner, poster, and watermark")
    brand.add_argument("--channel-name", required=True)
    brand.add_argument("--tagline", default="New science & technology stories every week")
    brand.add_argument("--accent", default="#00E5FF")
    brand.add_argument("--runtime-dir", default="runtime")

    seo = sub.add_parser("seo", help="generate SEO titles, description, chapters, and tags")
    seo.add_argument("--episode-dir", required=True)
    seo.add_argument("--topic", required=True)

    subs = sub.add_parser("subtitles", help="generate SRT and WebVTT subtitles from script.txt")
    subs.add_argument("--episode-dir", required=True)

    qa = sub.add_parser("qa", help="run pre-publish quality and compliance checks")
    qa.add_argument("--episode-dir", required=True)

    publish = sub.add_parser("publish-prep", help="prepare human-approved private YouTube upload package")
    publish.add_argument("--episode-dir", required=True)
    publish.add_argument("--approved-by", required=True)
    publish.add_argument("--publish-at")

    ab = sub.add_parser("ab-test", help="create title and thumbnail A/B variants")
    ab.add_argument("--topic", required=True)
    ab.add_argument("--experiment-id", default="exp-001")
    ab.add_argument("--runtime-dir", default="runtime")

    analytics = sub.add_parser("analytics", help="query Analytics and calculate a winner")
    analytics.add_argument("--experiment-file", required=True)
    analytics.add_argument("--start-date")
    analytics.add_argument("--end-date")
    analytics.add_argument("--credentials-file")
    analytics.add_argument("--token-file", default="runtime/youtube-token.json")
    analytics.add_argument("--notify", nargs="*", choices=["telegram", "email"])

    args = parser.parse_args()
    if args.command == "autopilot":
        path = run_autopilot(
            args.niche,
            channel_name=args.channel_name,
            episode_id=args.episode_id,
            runtime_dir=args.runtime_dir,
            approved_by=args.approved_by,
            publish_at=args.publish_at,
        )
        print(f"Created {path}")
    elif args.command == "demo":
        path = EpisodePipeline().create(args.topic, args.episode_id)
        print(f"Created {path}")
    elif args.command == "run":
        path = build_video(args.topic, args.runtime_dir, args.episode_id, video_mode=args.video_mode)
        print(f"Created {path}")
    elif args.command == "video-modes":
        print(json.dumps({"free_video_modes": list(FREE_VIDEO_MODES)}, indent=2))
    elif args.command == "trends":
        path = discover_trends(args.niche, args.runtime_dir, feeds=args.feeds, searxng_url=args.searxng_url)
        print(f"Created {path}")
    elif args.command == "branding":
        path = build_brand_kit(args.channel_name, args.tagline, args.runtime_dir, accent=args.accent)
        print(f"Created {path}")
    elif args.command == "seo":
        ep_dir = Path(args.episode_dir)
        script_text = (ep_dir / "script.txt").read_text(encoding="utf-8")
        path = write_seo_package(ep_dir, args.topic, script_text)
        print(f"Created {path}")
    elif args.command == "subtitles":
        ep_dir = Path(args.episode_dir)
        script_text = (ep_dir / "script.txt").read_text(encoding="utf-8")
        srt_path, vtt_path = write_subtitles(ep_dir, script_text)
        print(f"Created {srt_path} and {vtt_path}")
    elif args.command == "qa":
        report = evaluate_episode_qa(args.episode_dir)
        print(json.dumps(report, indent=2))
    elif args.command == "publish-prep":
        path = prepare_publish_package(args.episode_dir, approved_by=args.approved_by, publish_at=args.publish_at)
        print(f"Created {path}")
    elif args.command == "ab-test":
        path = create_experiment(args.topic, args.runtime_dir, args.experiment_id)
        print(f"Created {path}")
    elif args.command == "analytics":
        data = json.loads(open(args.experiment_file, encoding="utf-8").read())
        ids = [item["id"] for item in data["variants"]]
        start, end = args.start_date, args.end_date
        if not start or not end:
            start, end = date_window()
        metrics = YouTubeAnalyticsClient(args.credentials_file, args.token_file).query_variant_report(start, end, ids)
        path = snapshot_experiment(args.experiment_file, metrics)
        result = json.loads(path.read_text(encoding="utf-8")).get("analytics", {})
        print(f"Updated {path}")
        for warning in result.get("warnings", []):
            print(f"ALERT: {warning}")
        if result.get("warnings") and args.notify:
            for channel in send_alerts(args.experiment_file, args.notify):
                print(f"Notification sent: {channel}")
