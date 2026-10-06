# API layer

`app.py` builds the FastAPI application and owns the system's interface boundary. It serves the dashboard, validates incoming data, submits background workflows, streams state snapshots, handles approvals, updates demo tasks and schedules, and resets sample data.

## Important endpoints

| Method and path | Purpose |
| --- | --- |
| `POST /api/runs` | Validate and queue a new workflow |
| `GET /api/runs/{id}` | Read the latest persisted state |
| `GET /api/runs/{id}/events` | Stream state revisions with server-sent events |
| `POST /api/runs/{id}/cancel` | Cancel a queued or active run |
| `POST /api/runs/{id}/actions/{action}` | Approve or reject a proposed action |
| `PATCH /api/tasks/{id}` | Change local demo task completion |
| `PATCH /api/schedules/{name}` | Configure a daily automation |
| `POST /api/schedules/{name}/run` | Trigger an automation immediately |
| `GET /api/overview` | Populate dashboard context and integration status |

The FastAPI lifespan creates one `Store`, `Runtime`, and `Scheduler`. On shutdown it stops scheduling and cancels managed tasks cleanly.

This is a local, single-user API. Authentication and user-scoped authorization are required before public hosting. Keep route handlers thin: new reasoning belongs in agents, data access in services, and sequencing in graphs.

