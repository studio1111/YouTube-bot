import os

import pytest

from yt_agent.notifications import Alert, EmailNotifier, TelegramNotifier


pytestmark = pytest.mark.integration


@pytest.mark.skipif(
    os.getenv("RUN_LIVE_INTEGRATION") != "1" or not os.getenv("TELEGRAM_BOT_TOKEN") or not os.getenv("TELEGRAM_CHAT_ID"),
    reason="Set RUN_LIVE_INTEGRATION=1, TELEGRAM_BOT_TOKEN, and TELEGRAM_CHAT_ID to run the live Telegram sandbox test.",
)
def test_live_telegram_sandbox():
    TelegramNotifier().send(Alert("YouTube-bot sandbox test", "Telegram connector live sandbox test passed."))


@pytest.mark.skipif(
    os.getenv("RUN_LIVE_INTEGRATION") != "1"
    or not all(os.getenv(name) for name in ("SMTP_HOST", "SMTP_USERNAME", "SMTP_PASSWORD", "ALERT_TO_EMAIL")),
    reason="Set RUN_LIVE_INTEGRATION=1 and SMTP sandbox credentials to run the live SMTP test.",
)
def test_live_smtp_sandbox():
    EmailNotifier().send(Alert("YouTube-bot sandbox test", "SMTP connector live sandbox test passed."))
