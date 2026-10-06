# Current implementation

See README.md for the component inventory and startup. OpenAI generation and OpenRouter Jev decisions are required; simulated inference and Claude mode have been removed. API keys come from the existing root .env.

Real components: FastAPI, LangGraph, typed shared state, model output validation, SQLite history, SSE dashboard, local approval execution, scheduling, local memory/notifications, and the separately configured Discord client.

Remaining placeholders: synthetic integration data in services/fixtures.py and DemoServices, external Google/Prodigy/BeneFIT/GitHub adapters, email sending, external notifications, repository modification/code execution, and production authentication/hosting. Provider HTTP fixtures exist only under tests.
