#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
demo_python="${CAESAROS_PYTHON:-python3}"
if ! "$demo_python" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'; then
  echo 'CaesarOS needs Python 3.11+. Set CAESAROS_PYTHON to the newer Python executable.'
  exit 1
fi
if [ ! -x .venv-demo/bin/python ]; then
  "$demo_python" -m venv .venv-demo
fi
if ! .venv-demo/bin/python -c 'import fastapi, uvicorn, langgraph, apscheduler, httpx, dotenv' 2>/dev/null; then
  .venv-demo/bin/python -m pip install -r requirements.txt
fi
exec .venv-demo/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port "${CAESAROS_PORT:-8000}"
