# Services

`reasoning.py` makes real OpenAI Responses API calls; `jev.py` makes real OpenRouter Jev Decisions API calls. `model_outputs.py` defines validated generation contracts; `model_api.py` handles HTTP and provider usage accounting. There is no demo inference mode or template fallback.

`catalog.py` contains **DemoServices**, which still returns synthetic calendar, task, inbox, document, memory, training and repository data from SQLite. Its TODOs mark unfinished external adapters. Its `available_blocks` and `reserve` functions perform real time calculations and conflict-free allocation.

`fixtures.py` is the complete source of synthetic integration data. `store.py` handles real SQLite persistence and transactional local calendar approvals. Neither sends email, changes a real Google calendar, or edits a repository.

Every actual returned model call records provider/model/token usage in shared state. Keys remain server-side and are excluded from settings representations. See [integration setup](../../docs/INTEGRATIONS.md).
