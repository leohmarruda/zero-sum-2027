"""Vercel / local ASGI entrypoint — re-exports the FastAPI app."""

from app.main import app

__all__ = ["app"]
