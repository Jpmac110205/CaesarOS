# Backend entry point

This folder contains the compatibility ASGI entry point used by the launcher:

```bash
.venv-demo/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

`main.py` imports `create_app()` from `caesaros/api/app.py` and exposes the resulting FastAPI application as `app`. No business logic belongs here. The canonical backend package is `/caesaros`.

Keeping this thin module preserves the project's original `backend/main.py` path and makes deployment commands familiar. Tests build fresh app instances through `create_app(settings)` so each test can use its own temporary database.

