# Connect your ecosystem

The demo is complete without credentials. All services use synthetic local data. Routing and document relevance use explicit rules; agent summaries use templates unless Claude mode is enabled. None of the demo statuses indicate that a real app is connected.

## Live Claude reasoning (implemented)

1. Obtain an Anthropic API key and a model ID enabled in your account.
2. Add `CAESAROS_REASONER=claude`, `ANTHROPIC_API_KEY`, and `CAESAROS_CLAUDE_MODEL` to your existing `.env`. See `.env.example`; do not overwrite your existing keys.
3. Restart the server. `/api/health` will report `reasoner: claude`.

`caesaros/services/reasoning.py` calls the [Anthropic Messages API](https://platform.claude.com/docs/en/api/messages/create). Agent prompts live in your existing `agents/*/prompt.md` files. Claude receives the request, the agent's structured result, retrieved documents, and memory, and writes a summary. It also resolves medium-confidence routing into a whitelisted workflow. It cannot directly execute actions or change the deterministic schedule. Calls consume your Anthropic credits. Errors never silently switch back to demo reasoning.

TODO: For Bedrock, add a provider in `Reasoner.message` using your AWS account, region, enabled model ID, and IAM role. Normalize text and token usage into the same interface. The direct Anthropic provider is implemented; Bedrock is not.

## Jev (your model and contract needed)

TODO in `caesaros/decision/router.py`: connect your actual Jev inference interface. Its API/model format was not supplied, so this demo does not invent an endpoint.

Return `{workflow, confidence, reason, provider, gate}`. Validate workflow against `WORKFLOWS`. Scores ≥0.90 execute read/recommendation workflows, scores 0.65–0.89 escalate, and lower scores ask for clarification. Calendar writes always require user approval, regardless of routing score. Calibrate confidence on a held-out labeled request set before trusting it. Add Jev relevance and email classification adapters at the same bounded-decision layer.

## Prodigy Agents Mode

TODO: Mount a React Agents Mode page in your existing Prodigy frontend. This repository includes a standalone browser client as an executable preview, served by FastAPI; it does not modify or depend on the separate Prodigy repo.

Use a same-origin server proxy from Prodigy to CaesarOS. A minimal client submits a workflow and subscribes to persisted state snapshots:

```javascript
const run = await fetch('/caesaros/api/runs', {
  method: 'POST', headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({user_input: 'Figure out what I should do tonight.'})
}).then(r => r.json());
const events = new EventSource(`/caesaros/api/runs/${run.id}/events`);
events.addEventListener('state', event => {
  const state = JSON.parse(event.data);
  // Render state.agents, tool_results, sources, proposed_actions, final_response.
  if (['completed','awaiting_approval','failed','cancelled','needs_clarification']
      .includes(state.workflow_status)) events.close();
});
```

TODO in `DemoServices.documents` and `.memory` in `caesaros/services/catalog.py`: call your authenticated Prodigy retrieval and memory APIs. Normalize retrieval results to `id`, `title`, `content`, `tags`, and `source`. Preserve source/chunk identifiers. Keep ChromaDB, embeddings, reranking and ingestion inside Prodigy. Add user-scoped memory writes at `.review_memory`. The demo relevance filter is lexical, not vector search.

## BeneFIT

TODO in `DemoServices.fitness`: expose an authenticated BeneFIT endpoint for goals, workout history and the current training plan. Return the demo contract's `goal`, `weekly_sessions`, `last_workout`, `next_workout`, `duration_minutes`, and `exercises`. Keep Firebase access and permission rules inside BeneFIT. Do not put a Firebase admin credential in an agent or browser.

## Google Calendar, Tasks and Gmail

TODO in the three read methods in `caesaros/services/catalog.py`:

1. Create your Google Cloud OAuth app and enable Calendar, Tasks and Gmail APIs.
2. Configure your OAuth consent screen and redirect URI, then authorize your account.
3. Store refresh tokens on the backend and normalize results to the demo fixture contracts.
4. Preserve provider IDs. Calendar timestamps must have timezone offsets; handle recurrence and all-day events before calculating gaps.

The demo approval executor is the SQLite transaction in `Store.approve`. TODO: introduce a production calendar action adapter behind this executor, with provider idempotency keys, a fresh availability check, user-scoped OAuth and a durable action execution record. Keep approval and execution status separate for external requests that can fail. Do not simply replace the local append with an untracked API call.

Email replies are drafts only. TODO: add an `email.send` action schema and approval handler if you want sending. Task completion currently updates the local task store; connect it to Google Tasks explicitly. Calendar deletion and repository edits are not implemented.

## GitHub and Code Agent

TODO in `DemoServices.github`: select repositories and use a fine-grained read-only token to retrieve metadata, files and issues. The Code Agent currently receives sample repository context. Its coding → testing → critiquing stages produce an example/plan, test checklist and review notes; it does not run code or claim tests passed. Add an isolated execution service if actual test execution is needed.

## Discord (thin client implemented)

1. Create your bot in the Discord Developer Portal and enable Message Content Intent.
2. Invite it with permission to read/send messages in your chosen private channel.
3. Put `BOT_TOKEN`, numeric `DISCORD_OWNER_ID`, and numeric `DISCORD_CHANNEL_ID` in the root `.env`.
4. With the backend running, start `.venv-demo/bin/python -m connections.Discord.bot`.
5. Send `!caesar Can I fit a workout into my schedule today?` in that channel.

The bot accepts requests only from the configured owner/channel, calls the same workflow API, and returns the result. It never calls an LLM itself. It is not started or connected by the demo launcher. TODO in `DemoServices.notify`: add real scheduled Discord/Prodigy notification delivery and deduplication. Scheduled results currently go to the local notification feed.

## Before hosting or multi-user use

TODO: add authentication, user-scoped storage/services, secret management and authorization on every workflow and approval endpoint. The current backend is a single-user local demo and binds to `127.0.0.1`; no authentication or CORS policy for cross-origin clients is supplied. Do not expose it publicly as-is.

TODO: replace the single-process APScheduler with a dedicated scheduler/worker before adding multiple server workers. Only run one backend process today. Definitions and history persist in SQLite; live graph executions interrupted by a restart are marked failed and can be rerun. This is snapshot persistence, not automatic LangGraph checkpoint resume.

TODO: collect real labeled evaluation data for routing/retrieval, compare Claude-only vs Jev-assisted routing, and track calibrated confidence, retrieval precision/recall and provider-specific cost. The demo records latency, retries, tool results, model calls and actual Claude token usage; it does not invent dollar costs.
