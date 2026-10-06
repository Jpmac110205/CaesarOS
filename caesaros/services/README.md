# Shared services

Services are the boundary between reasoning code and data providers. Agents ask for normalized domain objects; services decide whether those objects come from local demo fixtures, Prodigy, BeneFIT, Google, GitHub, or another system.

## Files

- `catalog.py`: agent-facing service methods plus deterministic time-block helpers.
- `fixtures.py`: clearly labeled synthetic calendar, tasks, email, documents, fitness, repository context, and memory.
- `store.py`: SQLite persistence, transactions, approvals, schedule definitions, and local data changes.
- `reasoning.py`: optional Anthropic Messages API client and demo narration behavior.

The catalog methods are intentionally small. Replacing demo data should not require rewriting agents or the graph; preserve each method's normalized return shape.

`Store.approve()` is the only calendar action executor. It locks the database, verifies action status, rechecks the current calendar for conflicts, writes exactly once, and records the outcome. This makes approvals idempotent and rejects stale plans.

The reasoning provider receives a structured agent result and source context. It can improve narration but cannot directly write state or execute actions. Live provider failures surface as workflow failures rather than silently changing to demo behavior.

External credentials, OAuth refresh, rate-limit handling, provider IDs, and response normalization belong here. See `docs/INTEGRATIONS.md` for each adapter contract.

