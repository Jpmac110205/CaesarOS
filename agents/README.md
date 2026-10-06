# Agents

Each `run(state, ctx)` loads domain context through `tools.py` and writes a structured output to shared state. LangGraph controls the agent sequence. Agents call provider adapters through `ctx.reasoner` (OpenAI) and `ctx.jev` (OpenRouter Jev); they do not call other domain agents directly.

| Agent | Current implementation |
| --- | --- |
| Planner | OpenAI selects task priorities and focus items; Python allocates conflict-free time; OpenAI summarizes |
| Fitness | Python fits the supplied training plan into Planner availability; OpenAI explains the result |
| Tutor | Jev selects relevant candidate sources; OpenAI creates a lesson and practice questions |
| Email | Jev classifies messages; OpenAI creates a summary and reply draft |
| Code | OpenAI generates coding, proposed testing and critique results in three stages, then summarizes |

There are no fixed model responses. `prompt.md` files supply active model instructions. Structured generation contracts live in `caesaros/services/model_outputs.py`.

Context is still synthetic data from `DemoServices`; live model inference does not connect Google, Prodigy, BeneFIT or GitHub. Code and generated tests are not executed. Email drafts are not sent. Proposed calendar writes require approval and affect the local sample calendar.
