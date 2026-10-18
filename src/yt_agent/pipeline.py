from pathlib import Path
import json
from .models import EpisodeManifest


class EpisodePipeline:
    """Safe MVP pipeline: creates manifests only; no external publishing."""

    def __init__(self, runtime_dir: str = "runtime") -> None:
        self.runtime_dir = Path(runtime_dir)

    def create(self, topic: str, episode_id: str = "episode-001") -> Path:
        manifest = EpisodeManifest(episode_id=episode_id, topic=topic)
        target = self.runtime_dir / "episodes" / episode_id / f"v{manifest.version}"
        target.mkdir(parents=True, exist_ok=True)
        (target / "manifest.json").write_text(
            json.dumps(manifest.model_dump(mode="json"), indent=2), encoding="utf-8"
        )
        return target / "manifest.json"
