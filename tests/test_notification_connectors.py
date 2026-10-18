from unittest.mock import patch

from yt_agent.notifications import Alert, EmailNotifier, TelegramNotifier


class FakeHTTPResponse:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


def test_telegram_connector_posts_expected_payload():
    alert = Alert("Analytics warning", "Missing variant B")
    with patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "token", "TELEGRAM_CHAT_ID": "chat-123"}), \
         patch("yt_agent.notifications.urllib.request.urlopen", return_value=FakeHTTPResponse()) as open_url:
        TelegramNotifier().send(alert)

    request = open_url.call_args.args[0]
    body = request.data.decode()
    assert request.full_url == "https://api.telegram.org/bottoken/sendMessage"
    assert "chat_id=chat-123" in body
    assert "Missing+variant+B" in body


def test_smtp_connector_sends_expected_message():
    alert = Alert("Analytics warning", "Missing variant B")
    with patch.dict("os.environ", {
        "SMTP_HOST": "smtp.test", "SMTP_PORT": "2525", "SMTP_USERNAME": "bot@test",
        "SMTP_PASSWORD": "secret", "ALERT_FROM_EMAIL": "bot@test", "ALERT_TO_EMAIL": "owner@test",
    }), patch("yt_agent.notifications.smtplib.SMTP") as smtp_class:
        smtp = smtp_class.return_value.__enter__.return_value
        EmailNotifier().send(alert)

    smtp_class.assert_called_once_with("smtp.test", 2525, timeout=15)
    smtp.starttls.assert_called_once_with()
    smtp.login.assert_called_once_with("bot@test", "secret")
    sent = smtp.send_message.call_args.args[0]
    assert sent["Subject"] == "Analytics warning"
    assert sent["From"] == "bot@test"
    assert sent["To"] == "owner@test"
    assert "Missing variant B" in sent.get_content()


def test_connectors_fail_without_credentials():
    alert = Alert("Analytics warning", "Missing variant B")
    with patch.dict("os.environ", {}, clear=True):
        try:
            TelegramNotifier().send(alert)
        except RuntimeError as exc:
            assert "TELEGRAM_BOT_TOKEN" in str(exc)
        else:
            raise AssertionError("Telegram should require credentials")
        try:
            EmailNotifier().send(alert)
        except RuntimeError as exc:
            assert "SMTP_HOST" in str(exc)
        else:
            raise AssertionError("SMTP should require credentials")
