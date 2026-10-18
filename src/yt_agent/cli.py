import argparse
import json
from pathlib import Path

from .ab_test import create_experiment
from .analytics import YouTubeAnalyticsClient, date_window, snapshot_experiment
from .autopilot import run_autopilot
from .branding import build_brand_kit
from .content_calendar import write_calendar
from .health import write_health_report
from .idea_intelligence import build_idea_report
from .notifications import send_alerts
from .pipeline import EpisodePipeline
from .provenance import write_provenance
from .publisher import prepare_publish_package
from .qa import evaluate_episode_qa
from .scenario_prompts import write_scenario
from .seo import write_seo_package
from .subtitles import write_subtitles
from .trends import discover_trends
from .vertical_slice import build_video
from .video_engines import FREE_VIDEO_MODES
from .youtube_publish import YouTubePublisher, release_approval_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Autonomous local-first YouTube channel agent")
    sub = parser.add_subparsers(dest="command", required=True)
    ideas = sub.add_parser("ideas", help="collect and rank authorized public ideas from YouTube/Instagram/TikTok")
    ideas.add_argument("--niche", required=True); ideas.add_argument("--runtime-dir", default="runtime")
    scenario = sub.add_parser("scenario", help="generate a structured original episode scenario with local Ollama")
    scenario.add_argument("--idea-file", required=True); scenario.add_argument("--runtime-dir", default="runtime"); scenario.add_argument("--audience", default="curious science and technology viewers"); scenario.add_argument("--format", default="long-form")
    calendar = sub.add_parser("calendar", help="turn an idea report into a publishing calendar")
    calendar.add_argument("--ideas-file", required=True); calendar.add_argument("--start-date", required=True); calendar.add_argument("--runtime-dir", default="runtime"); calendar.add_argument("--weeks", type=int, default=4)
    health = sub.add_parser("health", help="check local tools and configured integrations")
    health.add_argument("--runtime-dir", default="runtime")
    provenance = sub.add_parser("provenance", help="hash every episode artifact into a provenance ledger")
    provenance.add_argument("--episode-dir", required=True)
    auto = sub.add_parser("autopilot", help="run complete pipeline: trends -> branding -> video -> A/B -> QA -> publish prep")
    auto.add_argument("--niche", required=True); auto.add_argument("--channel-name", default="Deep Cosmos"); auto.add_argument("--episode-id", default="ep-auto-001"); auto.add_argument("--runtime-dir", default="runtime"); auto.add_argument("--approved-by"); auto.add_argument("--publish-at")
    demo = sub.add_parser("demo", help="create a local episode manifest"); demo.add_argument("--topic", required=True); demo.add_argument("--episode-id", default="episode-001")
    run = sub.add_parser("run", help="generate script, audio, subtitles, SEO, visuals, QA, and MP4"); run.add_argument("--topic"); run.add_argument("--episode-id", default="episode-001"); run.add_argument("--runtime-dir", default="runtime"); run.add_argument("--video-mode", choices=list(FREE_VIDEO_MODES), default="ken-burns")
    modes = sub.add_parser("video-modes", help="list all 100% free video generation modes")
    trends = sub.add_parser("trends", help="discover and score video ideas for a niche"); trends.add_argument("--niche", required=True); trends.add_argument("--runtime-dir", default="runtime"); trends.add_argument("--searxng-url"); trends.add_argument("--feeds", nargs="*")
    brand = sub.add_parser("branding", help="generate SVG channel logo, banner, poster, and watermark"); brand.add_argument("--channel-name", required=True); brand.add_argument("--tagline", default="New science & technology stories every week"); brand.add_argument("--accent", default="#00E5FF"); brand.add_argument("--runtime-dir", default="runtime")
    seo = sub.add_parser("seo", help="generate SEO titles, description, chapters, and tags"); seo.add_argument("--episode-dir", required=True); seo.add_argument("--topic", required=True)
    subs = sub.add_parser("subtitles", help="generate SRT and WebVTT subtitles from script.txt"); subs.add_argument("--episode-dir", required=True)
    qa = sub.add_parser("qa", help="run pre-publish quality and compliance checks"); qa.add_argument("--episode-dir", required=True)
    publish = sub.add_parser("publish-prep", help="prepare human-approved private YouTube upload package"); publish.add_argument("--episode-dir", required=True); publish.add_argument("--approved-by", required=True); publish.add_argument("--publish-at")
    upload = sub.add_parser("upload-private", help="upload an approved package as private/unlisted"); upload.add_argument("--package", required=True); upload.add_argument("--credentials-file"); upload.add_argument("--token-file", default="runtime/youtube-upload-token.json")
    release = sub.add_parser("release-approval", help="record final human approval for public release in YouTube Studio"); release.add_argument("--episode-dir", required=True); release.add_argument("--approved-by", required=True)
    ab = sub.add_parser("ab-test", help="create title and thumbnail A/B variants"); ab.add_argument("--topic", required=True); ab.add_argument("--experiment-id", default="exp-001"); ab.add_argument("--runtime-dir", default="runtime")
    analytics = sub.add_parser("analytics", help="query Analytics and calculate a winner"); analytics.add_argument("--experiment-file", required=True); analytics.add_argument("--start-date"); analytics.add_argument("--end-date"); analytics.add_argument("--credentials-file"); analytics.add_argument("--token-file", default="runtime/youtube-token.json"); analytics.add_argument("--notify", nargs="*", choices=["telegram", "email"])
    args = parser.parse_args()
    if args.command == "ideas": print(f"Created {build_idea_report(args.niche, args.runtime_dir)}")
    elif args.command == "scenario":
        idea=json.loads(Path(args.idea_file).read_text(encoding='utf-8')); print(f"Created {write_scenario(idea, args.runtime_dir, args.audience, args.format)}")
    elif args.command == "calendar": print(f"Created {write_calendar(args.ideas_file, args.start_date, args.runtime_dir, args.weeks)}")
    elif args.command == "health": print(f"Created {write_health_report(args.runtime_dir)}")
    elif args.command == "provenance": print(f"Created {write_provenance(args.episode_dir)}")
    elif args.command == "autopilot": print(f"Created {run_autopilot(args.niche, channel_name=args.channel_name, episode_id=args.episode_id, runtime_dir=args.runtime_dir, approved_by=args.approved_by, publish_at=args.publish_at)}")
    elif args.command == "demo": print(f"Created {EpisodePipeline().create(args.topic, args.episode_id)}")
    elif args.command == "run": print(f"Created {build_video(args.topic, args.runtime_dir, args.episode_id, video_mode=args.video_mode)}")
    elif args.command == "video-modes": print(json.dumps({"free_video_modes": list(FREE_VIDEO_MODES)}, indent=2))
    elif args.command == "trends": print(f"Created {discover_trends(args.niche, args.runtime_dir, feeds=args.feeds, searxng_url=args.searxng_url)}")
    elif args.command == "branding": print(f"Created {build_brand_kit(args.channel_name, args.tagline, args.runtime_dir, accent=args.accent)}")
    elif args.command == "seo":
        ep_dir=Path(args.episode_dir); print(f"Created {write_seo_package(ep_dir, args.topic, (ep_dir/'script.txt').read_text(encoding='utf-8'))}")
    elif args.command == "subtitles":
        ep_dir=Path(args.episode_dir); print(f"Created {write_subtitles(ep_dir, (ep_dir/'script.txt').read_text(encoding='utf-8'))}")
    elif args.command == "qa": print(json.dumps(evaluate_episode_qa(args.episode_dir), indent=2))
    elif args.command == "publish-prep": print(f"Created {prepare_publish_package(args.episode_dir, approved_by=args.approved_by, publish_at=args.publish_at)}")
    elif args.command == "upload-private": print(json.dumps(YouTubePublisher(args.credentials_file, args.token_file).upload_private(args.package), indent=2))
    elif args.command == "release-approval": print(f"Created {release_approval_file(args.episode_dir, args.approved_by)}")
    elif args.command == "ab-test": print(f"Created {create_experiment(args.topic, args.runtime_dir, args.experiment_id)}")
    elif args.command == "analytics":
        data=json.loads(open(args.experiment_file, encoding='utf-8').read()); ids=[item['id'] for item in data['variants']]; start,end=args.start_date,args.end_date
        if not start or not end: start,end=date_window()
        path=snapshot_experiment(args.experiment_file, YouTubeAnalyticsClient(args.credentials_file,args.token_file).query_variant_report(start,end,ids)); result=json.loads(path.read_text(encoding='utf-8')).get('analytics',{}); print(f"Updated {path}")
        for warning in result.get('warnings',[]): print(f"ALERT: {warning}")
        if result.get('warnings') and args.notify:
            for channel in send_alerts(args.experiment_file,args.notify): print(f"Notification sent: {channel}")
