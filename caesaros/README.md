# CaesarOS core package

This package is the interface-independent backend. It coordinates routing, graph execution, agents, services, persistence, scheduled jobs, and API delivery.

## Request lifecycle

```mermaid
sequenceDiagram
    participant UI as Dashboard / Discord
    participant API as FastAPI
    participant RT as Runtime
    participant LG as LangGraph
    participant A as Agents
    participant S as Services
    participant DB as SQLite

    UI->>API: POST /api/runs
    API->>RT: submit validated RunRequest
    RT->>DB: save queued state
    RT->>LG: invoke workflow graph
    LG->>LG: route + confidence gate
    loop selected agent sequence
        LG->>A: run(state, context)
        A->>S: normalized tool request
        S-->>A: data
        A-->>LG: updated shared state
        RT->>DB: persist snapshot and events
        DB-->>UI: SSE state snapshot
    end
    LG->>RT: build response and proposed actions
    RT->>DB: save terminal snapshot
    DB-->>UI: result, sources, state, approvals
```

## Subpackages

| Folder | Responsibility |
| --- | --- |
| `api/` | HTTP routes, SSE stream, dashboard delivery |
| `decision/` | Workflow routing and document relevance |
| `graphs/` | LangGraph topology and managed execution runtime |
| `services/` | Data boundaries, reasoning provider, fixtures, persistence |
| `state/` | API models and complete graph-state schema |
| `scheduling/` | Morning, afternoon, and evening job definitions |
| `evaluation/` | Transparent routing smoke evaluation |

`config.py` reads environment settings and validates timezone/reasoner choices. `main.py` is an alternative ASGI entry point. The package does not import the frontend or Discord client into its reasoning logic, so new clients can use the same API.

