# Agents Mode dashboard

This folder is a dependency-free browser client served by FastAPI.

- `index.html` defines Command Center, History, Automations, and Integrations views.
- `styles.css` supplies the responsive desktop/mobile visual system.
- `app.js` owns API calls, SSE updates, safe rendering, action approvals, task changes, schedule controls, history, state export, and demo reset.
- `favicon.svg` is the local CaesarOS mark.

The browser posts a workflow, then subscribes to `/api/runs/{id}/events`. Every SSE event contains the latest persisted state snapshot. This lets the UI render routing decisions, queued/running/completed agents, activity, full shared state, retrieved sources, the final answer, and pending actions without duplicating orchestration logic.

All server content is escaped before insertion into HTML. The UI has no credentials and no direct provider access. It is a local preview of the Agents Mode that can later be rebuilt within Prodigy's React application against the same API.

There is no frontend build step. Start the backend and visit `http://127.0.0.1:8000`. When changing the UI, verify both wide and mobile layouts and test a complete workflow through action approval.

