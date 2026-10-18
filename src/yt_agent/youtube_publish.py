from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


class YouTubePublisher:
    """OAuth publisher: uploads private/unlisted only, never silently makes a video public."""

    def __init__(self, client_secret_file: str | None = None, token_file: str = "runtime/youtube-upload-token.json") -> None:
        self.client_secret_file = client_secret_file or os.getenv("YOUTUBE_CLIENT_SECRET_FILE")
        self.token_file = Path(token_file)

    def _credentials(self):
        if not self.client_secret_file:
            raise RuntimeError("Set YOUTUBE_CLIENT_SECRET_FILE before upload.")
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
        except ImportError as exc:
            raise RuntimeError("Install the optional [youtube] dependencies first.") from exc
        credentials = None
        if self.token_file.exists():
            credentials = Credentials.from_authorized_user_file(str(self.token_file), SCOPES)
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        if not credentials or not credentials.valid:
            flow = InstalledAppFlow.from_client_secrets_file(self.client_secret_file, SCOPES)
            credentials = flow.run_local_server(port=0)
            self.token_file.parent.mkdir(parents=True, exist_ok=True)
            self.token_file.write_text(credentials.to_json(), encoding="utf-8")
        return credentials

    def upload_private(self, package_file: str | Path) -> dict[str, Any]:
        package_path = Path(package_file)
        package = json.loads(package_path.read_text(encoding="utf-8"))
        status = package["youtube_insert_body"]["status"]
        requested = status.get("privacyStatus", "private")
        if requested not in {"private", "unlisted"}:
            raise ValueError("Upload worker only accepts private or unlisted status.")
        video_path = package_path.parent / "video.mp4"
        if not video_path.exists():
            raise FileNotFoundError("video.mp4 is required for YouTube upload.")
        try:
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
        except ImportError as exc:
            raise RuntimeError("Install the optional [youtube] dependencies first.") from exc
        service = build("youtube", "v3", credentials=self._credentials(), cache_discovery=False)
        request = service.videos().insert(
            part="snippet,status",
            body=package["youtube_insert_body"],
            media_body=MediaFileUpload(str(video_path), chunksize=1024 * 1024 * 8, resumable=True),
        )
        response = None
        while response is None:
            _, response = request.next_chunk()
        result = {"video_id": response.get("id"), "privacy_status": requested, "raw": response}
        (package_path.parent / "upload_result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        return result


def release_approval_file(episode_dir: str | Path, approved_by: str | None = None) -> Path:
    if not approved_by or not approved_by.strip():
        raise ValueError("A human approver is required before public release.")
    root = Path(episode_dir)
    upload_file = root / "upload_result.json"
    if not upload_file.exists():
        raise FileNotFoundError("Private upload must complete before release approval.")
    payload = {"approved_by": approved_by.strip(), "approved_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(), "video_id": json.loads(upload_file.read_text())["video_id"], "action": "release_in_youtube_studio"}
    out = root / "release_approval.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out
