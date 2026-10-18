from __future__ import annotations

import json
import os
import smtplib
import urllib.parse
import urllib.request
from dataclasses import dataclass
from email.message import EmailMessage
from typing import Iterable


@dataclass(frozen=True)
class Alert:
    subject: str
    body: str


def build_alert(experiment_file: str) -> Alert:
    data = json.loads(open(experiment_file, encoding="utf-8").read())
    analytics = data.get("analytics", {})
    warnings = analytics.get("warnings", [])
    if not warnings:
        raise ValueError("No Analytics warnings found.")
    subject = f"YouTube Analytics warning: {data.get('experiment_id', 'experiment')}"
    body = "\n".join([subject, "", *[f"- {warning}" for warning in warnings], "", f"Status: {analytics.get('result', {}).get('status', 'unknown')}"])
    return Alert(subject, body)


class TelegramNotifier:
    def __init__(self, bot_token: str | None = None, chat_id: str | None = None) -> None:
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")

    def send(self, alert: Alert) -> None:
        if not self.bot_token or not self.chat_id:
            raise RuntimeError("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID first.")
        payload = urllib.parse.urlencode({"chat_id": self.chat_id, "text": alert.body}).encode()
        request = urllib.request.Request(
            f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
            data=payload,
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=15) as response:
            if response.status != 200:
                raise RuntimeError(f"Telegram request failed: HTTP {response.status}")


class EmailNotifier:
    def __init__(self) -> None:
        self.host = os.getenv("SMTP_HOST")
        self.port = int(os.getenv("SMTP_PORT", "587"))
        self.username = os.getenv("SMTP_USERNAME")
        self.password = os.getenv("SMTP_PASSWORD")
        self.sender = os.getenv("ALERT_FROM_EMAIL") or self.username
        self.recipient = os.getenv("ALERT_TO_EMAIL")

    def send(self, alert: Alert) -> None:
        if not all([self.host, self.username, self.password, self.sender, self.recipient]):
            raise RuntimeError("Set SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD, ALERT_FROM_EMAIL, and ALERT_TO_EMAIL first.")
        message = EmailMessage()
        message["Subject"] = alert.subject
        message["From"] = self.sender
        message["To"] = self.recipient
        message.set_content(alert.body)
        with smtplib.SMTP(self.host, self.port, timeout=15) as smtp:
            smtp.starttls()
            smtp.login(self.username, self.password)
            smtp.send_message(message)


def send_alerts(experiment_file: str, channels: Iterable[str]) -> list[str]:
    alert = build_alert(experiment_file)
    delivered: list[str] = []
    for channel in channels:
        if channel == "telegram":
            TelegramNotifier().send(alert)
        elif channel == "email":
            EmailNotifier().send(alert)
        else:
            raise ValueError(f"Unknown notification channel: {channel}")
        delivered.append(channel)
    return delivered
