"""Compatibility entry point: python -m uvicorn backend.main:app."""
from caesaros.api.app import create_app
app = create_app()
