# Graph orchestration and runtime

This folder contains CaesarOS's execution engine.

`main_graph.py` defines a compiled LangGraph. Every run begins at `router`, may pass through `escalate`, follows the selected agent sequence, and ends at `respond`. Conditional edges use the workflow cursor to choose the next node. Agents communicate only by returning updates to the shared state.

`runtime.py` supplies the behavior around that topology:

- creates background tasks with a concurrency limit;
- marks the current agent and records events;
- wraps service calls as visible tool results;
- retries transient network/provider failures once;
- requires OpenAI summaries for Planner, Fitness and Code; other agents generate structured content directly;
- persists snapshots throughout execution;
- builds the final response and action proposals;
- handles cancellation, shutdown, and safe failure messages;
- marks runs interrupted by a server restart as failed.

The graph state is copied at node boundaries so partially failed agent work does not leak into a retry. SQLite snapshots provide history and live UI updates, but they are not LangGraph checkpoints capable of resuming inside a node after restart.

When adding a workflow, update the workflow registry and ensure every possible next agent is registered as a graph destination. When adding side effects, keep them outside normal agent nodes and behind explicit approval.

