import argparse
from .pipeline import EpisodePipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="YouTube channel agent scaffold")
    sub = parser.add_subparsers(dest="command", required=True)
    demo = sub.add_parser("demo", help="create a local episode manifest")
    demo.add_argument("--topic", required=True)
    demo.add_argument("--episode-id", default="episode-001")
    args = parser.parse_args()
    if args.command == "demo":
        path = EpisodePipeline().create(args.topic, args.episode_id)
        print(f"Created {path}")


if __name__ == "__main__":
    main()
