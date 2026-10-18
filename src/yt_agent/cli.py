import argparse
from .ab_test import create_experiment
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


if __name__ == "__main__":
    main()
