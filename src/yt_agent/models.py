from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha256
from pydantic import BaseModel, Field


def now() -> datetime:
    return datetime.now(timezone.utc)


class EpisodeState(StrEnum):
    IDEA = "idea"
    RESEARCHED = "researched"
    SCRIPT_DRAFT = "script_draft"
    SCRIPT_APPROVAL = "script_approval"
    ASSET_PRODUCTION = "asset_production"
    RENDERED = "rendered"
    QA = "qa"
    PUBLISH_APPROVAL = "publish_approval"
    PRIVATE_UPLOADED = "private_uploaded"
    RELEASED = "released"


class Source(BaseModel):
    url: str
    title: str = ""
    retrieved_at: datetime = Field(default_factory=now)
    license: str = "unknown"
    notes: str = ""


class EpisodeManifest(BaseModel):
    episode_id: str
    version: int = 1
    topic: str
    state: EpisodeState = EpisodeState.IDEA
    created_at: datetime = Field(default_factory=now)
    sources: list[Source] = Field(default_factory=list)
    artifacts: dict[str, str] = Field(default_factory=dict)
    approvals: list[str] = Field(default_factory=list)

    def digest(self) -> str:
        payload = self.model_dump_json().encode()
        return sha256(payload).hexdigest()
