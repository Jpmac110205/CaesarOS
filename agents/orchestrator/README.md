# Orchestrator compatibility layer

This folder preserves the original project's `agents/orchestrator` layout, but the actual orchestration is implemented as a LangGraph in `caesaros/graphs/`.

- `agent.py` exports `build_graph` for older imports.
- `tools.py` exports the workflow registry and bounded router.
- `prompt.md` documents the decision contract that a future Jev adapter must follow.

The orchestrator is deliberately not a conversational super-agent. It selects from an allowlist of workflows and lets graph edges control execution. This prevents one prompt from becoming responsible for routing, tools, state, retries, and final answers at the same time.

The routing gate has three outcomes:

| Confidence | Behavior |
| --- | --- |
| 0.90 or higher | Execute the selected read/recommendation workflow |
| 0.65–0.89 | Ask the configured reasoning provider to select an allowed workflow |
| Below 0.65 | Return a clarification request without running agents |

These demo scores come from transparent rules and are not calibrated model probabilities. The real router lives in `caesaros/decision/router.py`; replace its adapter when Jev's invocation contract is available.

