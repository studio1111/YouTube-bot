from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class VariantMetrics:
    variant_id: str
    impressions: int
    views: int
    ctr: float


@dataclass(frozen=True)
class WinnerResult:
    status: str
    winner: str | None
    reason: str
    metrics: list[VariantMetrics]


def calculate_winner(metrics: list[VariantMetrics], min_impressions: int = 100) -> WinnerResult:
    if len(metrics) < 2:
        return WinnerResult("insufficient_data", None, "At least two variants are required.", metrics)
    if any(item.impressions < min_impressions for item in metrics):
        return WinnerResult(
            "insufficient_data", None,
            f"Each variant needs at least {min_impressions} impressions.", metrics,
        )
    ordered = sorted(metrics, key=lambda item: (item.ctr, item.impressions), reverse=True)
    if ordered[0].ctr == ordered[1].ctr:
        return WinnerResult("tie", None, "The top variants have identical CTR.", metrics)
    return WinnerResult("winner_found", ordered[0].variant_id, "Highest CTR after minimum sample.", metrics)


def _extract_rows(payload: dict[str, Any], variant_ids: list[str]) -> list[VariantMetrics]:
    rows = payload.get("rows", [])
    # The API does not attribute impressions to thumbnail variants. This adapter
    # expects a dimension named variant, supplied by an approved experiment proxy
    # or an exported experiment-level report.
    result: list[VariantMetrics] = []
    for row in rows:
        values = row if isinstance(row, list) else row.get("values", [])
        if len(values) < 4:
            continue
        variant, impressions, views, ctr = values[:4]
        if variant not in variant_ids:
            continue
        result.append(VariantMetrics(variant, int(impressions), int(views), float(ctr)))
    return result


class YouTubeAnalyticsClient:
    """Optional Google client. Imports are lazy so the free offline path still works."""

    def __init__(self, credentials_file: str | None = None, token_file: str = "runtime/youtube-token.json") -> None:
        self.credentials_file = credentials_file or os.getenv("YOUTUBE_CLIENT_SECRET_FILE")
        self.token_file = Path(token_file)

    def query_variant_report(self, start_date: str, end_date: str, variant_ids: list[str]) -> list[VariantMetrics]:
        if not self.credentials_file:
            raise RuntimeError("Set YOUTUBE_CLIENT_SECRET_FILE before connecting to Analytics.")
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
        except ImportError as exc:
            raise RuntimeError("Install the youtube optional dependencies first.") from exc

        scopes = ["https://www.googleapis.com/auth/yt-analytics.readonly"]
        credentials = None
        if self.token_file.exists():
            credentials = Credentials.from_authorized_user_file(str(self.token_file), scopes)
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        if not credentials or not credentials.valid:
            flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, scopes)
            credentials = flow.run_local_server(port=0)
            self.token_file.parent.mkdir(parents=True, exist_ok=True)
            self.token_file.write_text(credentials.to_json(), encoding="utf-8")

        service = build("youtubeAnalytics", "v2", credentials=credentials, cache_discovery=False)
        response = service.reports().query(
            ids="channel==MINE",
            startDate=start_date,
            endDate=end_date,
            metrics="impressions,views,impressionsClickThroughRate",
            dimensions="variant",
            sort="-impressions",
        ).execute()
        return _extract_rows(response, variant_ids)


def snapshot_experiment(experiment_file: str, metrics: list[VariantMetrics], output_file: str | None = None) -> Path:
    path = Path(experiment_file)
    data = json.loads(path.read_text(encoding="utf-8"))
    result = calculate_winner(metrics)
    data["analytics"] = {
        "metrics": [item.__dict__ for item in metrics],
        "result": {
            "status": result.status,
            "winner": result.winner,
            "reason": result.reason,
        },
    }
    target = Path(output_file) if output_file else path
    target.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return target


def date_window(days: int = 7) -> tuple[str, str]:
    end = date.today()
    return ((end - timedelta(days=days - 1)).isoformat(), end.isoformat())
