# Discord client

`bot.py` is a thin secondary interface to the CaesarOS backend. It contains no agent logic and makes no LLM calls.

After configuration, the bot accepts messages beginning with `!caesar` from one configured owner in one configured channel. It posts the request to `POST /api/runs`, polls the resulting run until it reaches a terminal status, and sends the final response in Discord-sized chunks. Proposed actions must still be reviewed in the Agents Mode dashboard.

Required `.env` values:

```dotenv
BOT_TOKEN=...
DISCORD_OWNER_ID=123456789
DISCORD_CHANNEL_ID=123456789
CAESAROS_API_URL=http://127.0.0.1:8000
```

Start the backend first, then run:

```bash
.venv-demo/bin/python -m connections.Discord.bot
```

The client ignores other users, other channels, bot messages, and ordinary messages. The local `.env` file in this folder is legacy; use the root `.env` and never commit credentials. Scheduled outbound Discord notifications are a separate TODO in the notification service.

