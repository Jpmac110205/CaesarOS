# Google integration placeholder

This folder reserves space for Google-specific setup or OAuth callback code. The demo does not access a real Google account.

The production integration will support three separate service contracts:

- Calendar: timezone-aware events with provider IDs, start, end, title, recurrence handling, and all-day semantics.
- Tasks: task IDs, titles, deadlines, priority, estimated duration, and completion state.
- Gmail: message IDs, sender, subject, safe text body, category, action requirement, and extracted deadline.

OAuth tokens must remain on the backend and be scoped to the current user. Begin with read-only scopes. Calendar creation, task updates, and email sending need explicit action schemas, approval, idempotency keys, and durable provider execution records.

The current adapter TODOs are in `caesaros/services/catalog.py`, while local calendar approval behavior is in `caesaros/services/store.py`. Detailed setup guidance is in `docs/INTEGRATIONS.md`.

