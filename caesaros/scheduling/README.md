# Scheduled workflows

`scheduler.py` wraps APScheduler for three autonomous workflows:

- `morning_digest` at 8:00 AM;
- `afternoon_checkin` at 2:00 PM;
- `evening_review` at 9:00 PM.

Schedules are stored in SQLite, restored when FastAPI starts, and interpreted in `CAESAROS_TIMEZONE`. The dashboard can enable them, change hour/minute, or run them immediately.

A scheduled trigger submits the same validated `RunRequest` used by the web interface. It therefore uses the same router, graph, state, services, history, and error handling. Digest results are also saved in the local notification feed. Calendar changes still require approval.

This scheduler is appropriate for a single local backend process. Do not launch multiple Uvicorn workers: every worker would own a scheduler and could duplicate jobs. Before distributed deployment, move scheduling and execution to a dedicated worker system with durable claims, retries, and notification delivery.

