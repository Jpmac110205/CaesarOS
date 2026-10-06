# CaesarOS

A local personal assistant backend: FastAPI → Jev decisions through OpenRouter → LangGraph → OpenAI-powered agents → shared services. The dashboard shows execution, shared state, sources, proposals and history.

**Inference requires working API keys. There is no simulated LLM or offline fallback.** OpenAI generates responses and structured agent content. Jev performs routing, document relevance and email classification through OpenRouter's Decisions API.

## What is implemented and what is sample data?

| Component | Current behavior |
| --- | --- |
| OpenAI reasoning | Real Responses API calls for planning choices, tutoring, email drafts, coding, test proposals, critique and summaries |
| Jev decisions | Real OpenRouter Decisions API calls; confidence and probabilities come from Jev |
| Workflow execution | Real LangGraph nodes, conditional edges, isolated state, bounded retries and cancellation |
| Scheduling and persistence | Real APScheduler jobs and SQLite snapshots, tasks, memory and local notifications |
| Time allocation | Python computes free windows, reserves model-selected focus items and inserts buffers |
| Approvals | Real transactional, idempotent local calendar writes with fresh conflict checks |
| Calendar, tasks, inbox, documents, preferences, training and repository context | **Synthetic fixtures** in `caesaros/services/fixtures.py`, accessed by `DemoServices` |
| Google, Prodigy, BeneFIT and GitHub connections | **Unimplemented adapters** in `caesaros/services/catalog.py` |
| Code execution and repository editing | **Unimplemented**; code, proposed tests and critique are model-generated, `executed` remains false |
| Sending email and external scheduled notifications | **Unimplemented**; replies remain drafts and scheduled results stay in the local feed |
| Discord | Implemented API client; requires separate bot setup and startup |

See [integration details](docs/INTEGRATIONS.md) for provider endpoints and unfinished adapter boundaries. The original [project overview](docs/PROJECT_OVERVIEW.txt) is a historical design document; its Claude/Bedrock references do not describe the current OpenAI implementation.

## Run

Requires Node.js 18+ and Python 3.11+. Add these to your existing `.env`:

```dotenv
OPENAI_API_KEY=your-openai-key
JEV_API_KEY=your-openrouter-key
CAESAROS_OPENAI_MODEL=gpt-4.1-mini
CAESAROS_JEV_MODEL=typesafe/jev-1.13
```

`OpenAI_API_KEY` and `Jev_API_KEY` are accepted aliases. `OPENROUTER_API_KEY` is also accepted for Jev. Models are configurable; the values above are defaults. Existing process environment values take precedence over `.env`. The backend rejects missing keys before startup. Old `CAESAROS_REASONER=demo/claude` settings no longer select a provider: OpenAI is always used.

```bash
npm run dev
```

This starts both the dashboard and API in one terminal, with automatic backend reload. No `npm install` is needed: the launcher uses Node's built-in modules. On first use it creates `.venv-demo` if necessary and installs Python dependencies. Later starts reuse the environment; dependency changes trigger installation. It leaves your existing `.env` untouched. Refresh the browser after HTML, CSS or JavaScript edits; Ctrl+C stops the server and reload worker.

Open **http://127.0.0.1:8000**; API documentation is at **http://127.0.0.1:8000/docs**. For a different Python when creating the environment: `CAESAROS_PYTHON=/path/to/python3.11 npm run dev`. For another port: `CAESAROS_PORT=8001 npm run dev`.

The existing `./run_demo.sh` remains available for compatibility. Manual startup:

```bash
python3 -m venv .venv-demo
.venv-demo/bin/python -m pip install -r requirements.txt
.venv-demo/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Run one server process so scheduled jobs run once. Calls consume OpenAI and OpenRouter credits, including scheduled workflows. Provider failures mark workflows failed; they never return a canned success. The configured status shown in Integrations means credentials were loaded, not that a live request has been verified.

## Request lifecycle

1. Jev selects an allowed workflow and returns confidence and probabilities. Explicit user workflow selection bypasses routing and reports no model confidence.
2. Confidence ≥0.90 executes; 0.65–0.89 asks OpenAI to resolve the choice; lower confidence or an unsupported goal asks for clarification. These are application thresholds, not a measured accuracy claim.
3. LangGraph runs the registered agents in sequence through shared state.
4. Agents retrieve labeled sample context, call real providers and validate structured results. Python allocates focus items and workouts into free windows.
5. The response builder combines actual outputs and proposes calendar actions. Approval executes only against the local SQLite calendar.

`metrics.provider_calls` records the actual returned model, response ID, token usage, and provider-reported cost when available. Failed or incomplete responses and refusals are errors. No dollar cost is invented for OpenAI.

Plans use the stored sample day's 5 PM–10:30 PM window. The date remains stable until reset; this is not your live calendar. `CAESAROS_TIMEZONE` defaults to `America/New_York`. Interrupted executions are marked failed after restart; snapshot persistence does not resume an agent mid-execution.

Existing historical runs are preserved. The dashboard labels earlier simulated or Claude runs so they cannot be confused with new live inference.

## Code guide

| Path | Responsibility |
| --- | --- |
| `caesaros/config.py` | Environment keys, models, timezone and database |
| `caesaros/services/reasoning.py` | OpenAI Responses API and structured generation |
| `caesaros/services/jev.py` | OpenRouter Jev API and typed decision validation |
| `caesaros/services/model_outputs.py` | Pydantic output contracts |
| `caesaros/decision/` | Workflow allowlist, confidence gates and Jev relevance |
| `caesaros/graphs/` | LangGraph and runtime, state persistence, retries, responses |
| `agents/` | Domain agents and prompts; Code has coding/testing/critiquing stages |
| `caesaros/services/catalog.py` | Sample data adapter boundaries and real time calculations |
| `caesaros/services/store.py` | SQLite storage and local action execution |
| `caesaros/scheduling/` | Persistent daily workflow definitions |
| `frontend/` | Dashboard, SSE, approvals, history and JSON export |
| `tests/` | Offline HTTP fixtures and provider/workflow tests; no production mock switch |

## API

| Endpoint | Behavior |
| --- | --- |
| `POST /api/runs` | Submit `{user_input, workflow?: "auto"}`; returns 202 and run ID |
| `GET /api/runs` | Latest 50 full workflow records |
| `GET /api/runs/{id}` | Persisted state snapshot |
| `GET /api/runs/{id}/events` | SSE snapshots until terminal state |
| `POST /api/runs/{id}/cancel` | Cancel execution |
| `POST /api/runs/{id}/actions/{action_id}` | Approve/reject a local calendar proposal |
| `PATCH /api/tasks/{id}` | Update local task completion |
| `PATCH /api/schedules/{name}` | Set enabled, hour and minute |
| `POST /api/schedules/{name}/run` | Run a scheduled workflow now |
| `GET /api/overview` | Sample context, schedules, provider configuration and metrics |
| `GET /api/health` | Backend health and configured models; does not test provider connectivity |
| `POST /api/demo/reset` | Restore sample data and invalidate pending proposals; history stays |

Workflows: `workout`, `study`, `interview`, `daily_plan`, `tutor`, `email`, `code`, `morning_digest`, `afternoon_checkin`, `evening_review`. Routing is a model decision, so example wording does not guarantee a particular confidence gate.

## Verify

```bash
.venv-demo/bin/python -m pip install -r requirements-dev.txt
.venv-demo/bin/python -m pytest -q
```

Tests use temporary databases and mocked HTTP responses **only in tests**. They verify request formats, structured output validation, provider failures, real graph execution, scheduling, approval conflicts/idempotency, retries, persistence, SSE and cancellation. They do not verify credential validity or live model quality.

For a separate live routing smoke evaluation (consumes OpenRouter credits):

```bash
.venv-demo/bin/python -m caesaros.evaluation.routing_eval
```

Provider references: [OpenAI structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses), [OpenRouter Jev tutorial](https://openrouter.ai/docs/guides/community/jev-tutorial).
