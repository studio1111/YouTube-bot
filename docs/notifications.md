# Alert notifications

Analytics warnings can be delivered through Telegram or SMTP email. Both use free protocols/APIs, but SMTP or a mail provider may impose its own limits.

## Telegram

1. Create a bot with BotFather.
2. Send it one message from the target chat.
3. Obtain the chat ID.
4. Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in a local `.env`.

## Email

Set SMTP credentials locally:

```env
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=alerts@example.com
SMTP_PASSWORD=app-password
ALERT_FROM_EMAIL=alerts@example.com
ALERT_TO_EMAIL=you@example.com
```

## Run

```bash
yt-agent analytics --experiment-file runtime/experiments/sky-001/experiment.json --notify telegram email
```

Notifications are sent only when the Analytics snapshot contains warnings. Credentials are read from environment variables and never written to manifests.
