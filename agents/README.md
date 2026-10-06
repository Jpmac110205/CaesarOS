# Agents

This folder contains CaesarOS's specialized reasoning components. An agent interprets domain data and writes a structured result into the workflow's shared state. Agents do not choose the overall workflow, call one another, persist state, or talk directly to external APIs.

## How agents run

1. The router selects a named workflow such as `study` or `interview`.
2. LangGraph converts that workflow into an ordered agent sequence.
3. The runtime imports each agent's `run(state, ctx)` function.
4. The agent reads earlier outputs from `state` and obtains data through its `tools.py` wrapper.
5. It writes one output field, such as `planner_output` or `fitness_output`.
6. The runtime records status, duration, attempts, events, and optional model usage before advancing the graph.

This shared-state pattern is the central coupling rule. For example, the Planner writes available time to `planner_output`; the Fitness Agent later reads that field. Planner never imports or invokes Fitness.

## Folder convention

Each agent normally contains:

- `agent.py`: deterministic domain logic and the `run` entry point.
- `tools.py`: narrow service calls exposed to that agent.
- `prompt.md`: instructions used when live Claude reasoning is enabled.

The default demo remains useful without an LLM. Python creates structured outputs and local templates summarize them. In Claude mode, the same structured result and relevant sources are sent to the model for narration; the model cannot change Python's validated schedule or execute an action.

## Agents

| Folder | State written | Main role |
| --- | --- | --- |
| `email/` | `email_output` | Prioritize messages, extract actions, prepare drafts |
| `planner/` | `planner_output` | Find free time and allocate priorities |
| `tutor/` | `tutor_output`, retrieved documents | Explain course material using Prodigy-like sources |
| `fitness/` | `fitness_output` | Fit a workout into planner availability |
| `code/` | `code_output` | Produce an implementation or interview-prep artifact |
| `orchestrator/` | none directly | Compatibility entry point and routing documentation |

To add an agent, add its state fields, create its folder and `run` function, register the node and possible destinations in `caesaros/graphs/main_graph.py`, and add it to the relevant sequence in `caesaros/decision/router.py`. Keep provider-specific code in `caesaros/services/`.

