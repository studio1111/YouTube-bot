# Alert notifications

Analytics warnings can be delivered through Telegram or SMTP email. Both use free protocols/APIs, but SMTP or a mail provider may impose its own limits.

## Telegram

1. Create a dedicated test bot with BotFather.
2. Send it one message from the target test chat.
3. Obtain the chat ID.
4. Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` locally.

## Email

Use a disposable SMTP sandbox such as a local MailHog/Mailpit instance or a provider's test inbox. Never use a production recipient for the live test.

```env
RUN_LIVE_INTEGRATION=1
TELEGRAM_BOT_TOKEN=test-bot-token
TELEGRAM_CHAT_ID=test-chat-id
SMTP_HOST=127.0.0.1
SMTP_PORT=1025
SMTP_USERNAME=test
SMTP_PASSWORD=test
ALERT_FROM_EMAIL=alerts@example.test
ALERT_TO_EMAIL=inbox@example.test
```

## Run live sandbox checks

```bash
RUN_LIVE_INTEGRATION=1 \
TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN" \
TELEGRAM_CHAT_ID="$TELEGRAM_CHAT_ID" \
SMTP_HOST=127.0.0.1 SMTP_PORT=1025 \
SMTP_USERNAME=test SMTP_PASSWORD=test \
ALERT_FROM_EMAIL=alerts@example.test ALERT_TO_EMAIL=inbox@example.test \
python -m pytest -q tests/test_live_notifications.py -m integration
```

The tests are opt-in and skipped by default, so normal CI never sends external messages. Telegram has no official universal sandbox, so use a dedicated test bot and chat; SMTP should point to MailHog/Mailpit or another disposable test inbox. Credentials are read only from environment variables and never committed.
