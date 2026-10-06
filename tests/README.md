# Tests

Run `.venv-demo/bin/python -m pytest -q`. Tests exercise the real FastAPI app, LangGraph runtime, SQLite store, scheduler, source handling, approvals, persistence, retries, cancellation and SSE using temporary databases.

`conftest.py` installs mocked HTTP transports **only for tests**. Production has no mock-provider setting or offline inference path. `test_reasoning.py` verifies live OpenAI/OpenRouter request contracts, credential headers, usage accounting, structured validation, confidence gates, and failure/refusal handling without spending credits.

These tests do not establish live credential validity or model quality. `caesaros.evaluation.routing_eval` separately makes real Jev calls when explicitly run.
