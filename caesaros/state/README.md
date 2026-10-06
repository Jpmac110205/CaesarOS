# Workflow state

This folder defines the data contracts shared by the API, graph, agents, UI, and persistence layer.

`models.py` contains Pydantic request models. These reject unknown fields, validate workflow names, limit request length, constrain schedule time, and restrict approval decisions to `approve` or `reject`.

`workflow_state.py` defines the complete LangGraph `WorkflowState` and the `new_state()` factory. Every request gets a fresh ID and independent containers for:

- routing decision, confidence, selected workflow, cursor, and status;
- per-agent status, attempts, summary, and duration;
- normalized calendar, tasks, email, memory, documents, fitness, and GitHub context;
- every specialized agent output;
- tool results, source citations, events, proposed actions, metrics, and final response.

`TERMINAL` identifies statuses that stop SSE streaming: completed, awaiting approval, needs clarification, failed, and cancelled. `awaiting_approval` is terminal execution state because reasoning is finished; approving an action updates the persisted record separately.

Add fields deliberately. They become part of persisted JSON and the browser-visible debugging contract. Prefer structured dictionaries and lists over opaque prose so later agents can consume outputs reliably.

