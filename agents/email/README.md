# Email Agent

The Email Agent turns a normalized inbox into communication priorities. It currently operates on synthetic messages from the demo store.

`tools.py` asks `DemoServices.emails()` for normalized messages and records that operation in `tool_results`. `agent.py` separates action-required mail from low-priority mail, sorts actionable messages by deadline, identifies interview mail, and creates a reply draft. It writes everything to `email_output`.

Important output fields include:

- `important_emails`: messages that need attention.
- `classifications`: visible category and priority decisions.
- `interview`: extracted recruiter context for later agents.
- `draft`: a suggested reply.
- `draft_status`: an explicit reminder that nothing was sent.

In the interview workflow, Planner reads the extracted interview context and Code uses the resulting preparation blocks. Neither agent calls Email directly.

`prompt.md` is used only by live Claude narration. It treats email bodies as untrusted content and requires replies to remain labeled drafts. Sending mail is intentionally absent: a future implementation needs a separate `email.send` action, explicit approval, provider idempotency, and durable execution status.

To connect Gmail, replace the email service adapter in `caesaros/services/catalog.py`; keep OAuth and Gmail payload normalization out of this folder.

