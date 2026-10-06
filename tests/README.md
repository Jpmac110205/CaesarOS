# Tests

The tests exercise the real FastAPI application, LangGraph, SQLite store, scheduler, services, and agent sequence. Each test uses a temporary database so it does not modify your local demo state.

Run the suite from the repository root:

```bash
.venv-demo/bin/python -m pytest -q
```

`test_workflows.py` covers:

- expected agent chains for workout, study, interview, and daily-plan workflows;
- shared-state isolation between simultaneous requests;
- conflict-free schedule allocation and study buffers;
- retrieval sources and missing-context behavior;
- confidence execution, escalation, and clarification gates;
- action idempotency, stale-plan conflict rejection, and reset invalidation;
- task completion, scheduled review memory, notifications, persistence, and timezone restoration;
- SSE, validation, transient retry, safe permanent failure, and cancellation.

`test_reasoning.py` uses a mock HTTP transport to verify the live Claude request shape, token accounting, structured-result grounding, workflow allowlisting, and visible provider failures without spending API credits.

Add tests at layer boundaries where failures would change observable behavior. Avoid tests that merely repeat an implementation line without protecting a contract.

