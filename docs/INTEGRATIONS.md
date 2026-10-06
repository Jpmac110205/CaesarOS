# Connect your ecosystem

Inference is live and requires keys. Other integrations still supply labeled synthetic local data. See the component inventory in [README](../README.md).

## OpenAI (implemented)

Set `OPENAI_API_KEY` (or `OpenAI_API_KEY`) in the root `.env`. `CAESAROS_OPENAI_MODEL` defaults to `gpt-4.1-mini`.

`caesaros/services/reasoning.py` calls `POST https://api.openai.com/v1/responses`. It generates structured planning choices, tutor lessons and practice questions, email summaries and drafts, coding artifacts, test proposals, and critiques. Planner/Fitness/Code summaries and medium-confidence routing resolution also use OpenAI. Structured content is validated with Pydantic contracts in `model_outputs.py`. Python owns time allocation, approvals and execution facts. Provider refusals, incomplete results, invalid output, and HTTP failures do not fall back to templates.

The [official OpenAI documentation](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses) describes the Responses API structured output format used here. Claude and Bedrock are not implemented providers in the current application.

## Jev through OpenRouter (implemented)

Set `JEV_API_KEY` (or `Jev_API_KEY` / `OPENROUTER_API_KEY`) to an **OpenRouter key**. `CAESAROS_JEV_MODEL` defaults to `typesafe/jev-1.13`.

`caesaros/services/jev.py` calls `POST https://openrouter.ai/api/alpha/decisions` with Bearer authentication, `model`, `state`, and typed `questions`. Workflow routing uses a Choice question and retains returned confidence and probabilities. Relevance and action-required classification use Noul probabilities. Email categories use Choice. Jev returns decisions, not generated explanations; the UI says which choice it selected.

This uses the actual decision model, rather than OpenRouter's separate `typesafe/jev-router` product that chooses a downstream chat model. The [OpenRouter Jev tutorial](https://openrouter.ai/docs/guides/community/jev-tutorial) documents this endpoint and response shape.

Scores ≥0.90 execute, 0.65–0.89 escalate to OpenAI, and lower confidence asks for clarification. Choosing `clarify` also asks for clarification. These thresholds are application policy and need evaluation on real labeled requests. Explicit workflows bypass Jev routing and carry `confidence: null`. Calendar writes require approval regardless of confidence.

Provider configuration is reported as `configured` before connectivity is verified. Each actual returned call is recorded in `metrics.provider_calls`, including model, usage, response ID and cost when supplied by OpenRouter. Your existing `.env` is not overwritten.

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

TODO in `DemoServices.documents` and `.memory` in `caesaros/services/catalog.py`: call your authenticated Prodigy retrieval and memory APIs. Normalize retrieval results to `id`, `title`, `content`, `tags`, and `source`. Preserve source/chunk identifiers. Keep ChromaDB, embeddings, reranking and ingestion inside Prodigy. Add user-scoped memory writes at `.review_memory`. Candidate relevance is evaluated by live Jev Noul questions; vector search and ingestion remain unimplemented here.

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

TODO in `DemoServices.github`: select repositories and use a fine-grained read-only token to retrieve metadata, files and issues. The Code Agent currently receives sample repository context. Its coding → testing → critiquing stages call OpenAI to generate an artifact/plan, proposed tests and review notes; it does not run code or claim tests passed. Add an isolated execution service if actual test execution is needed.

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

TODO: collect real labeled evaluation data for routing/retrieval, compare OpenAI-only vs Jev-assisted routing, and track calibrated confidence, retrieval precision/recall and provider-specific cost. The demo records latency, retries, tool results, model calls and actual OpenAI and Jev token usage plus provider-reported Jev cost; it does not invent dollar costs.
