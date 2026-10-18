import argparse
import json
from .ab_test import create_experiment
from .analytics import YouTubeAnalyticsClient, date_window, snapshot_experiment
from .notifications import send_alerts
from .pipeline import EpisodePipeline
from .vertical_slice import build_video


def main() -> None:
    parser = argparse.ArgumentParser(description="YouTube channel agent scaffold")
    sub = parser.add_subparsers(dest="command", required=True)
    demo = sub.add_parser("demo", help="create a local episode manifest")
    demo.add_argument("--topic", required=True)
    demo.add_argument("--episode-id", default="episode-001")
    run = sub.add_parser("run", help="generate a local script, slides, and MP4")
    run.add_argument("--topic")
    run.add_argument("--episode-id", default="episode-001")
    run.add_argument("--runtime-dir", default="runtime")
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
    if args.command == "demo":
        path = EpisodePipeline().create(args.topic, args.episode_id)
        print(f"Created {path}")
    elif args.command == "run":
        path = build_video(args.topic, args.runtime_dir, args.episode_id)
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
