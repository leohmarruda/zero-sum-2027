"""SQLAlchemy async engine and session factory."""

from __future__ import annotations

import logging
import os
from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

logger = logging.getLogger(__name__)

_DEFAULT_SQLITE = "sqlite+aiosqlite:///./dev.db"
_VERCEL_SQLITE = "sqlite+aiosqlite:////tmp/zero-sum.db"


class Base(DeclarativeBase):
    pass


def _strip_quotes(value: str) -> str:
    return value.strip().strip('"').strip("'")


def _turso_async_url(turso_url: str) -> str:
    """Map libsql://host → sqlite+aiolibsql://host for sqlalchemy-libsql."""
    host = _strip_quotes(turso_url)
    for prefix in ("libsql://", "https://", "http://"):
        if host.startswith(prefix):
            host = host[len(prefix) :]
            break
    return f"sqlite+aiolibsql://{host}?secure=true"


def _sqlite_url() -> str:
    if os.environ.get("VERCEL"):
        return _VERCEL_SQLITE
    settings = get_settings()
    return settings.database_url or _DEFAULT_SQLITE


@lru_cache
def get_engine() -> AsyncEngine:
    settings = get_settings()
    turso = _strip_quotes(settings.turso_database_url)
    token = _strip_quotes(settings.turso_auth_token)

    if turso:
        try:
            # Registers the sqlite+aiolibsql dialect when installed.
            import sqlalchemy_libsql  # noqa: F401

            return create_async_engine(
                _turso_async_url(turso),
                echo=False,
                connect_args={"auth_token": token} if token else {},
            )
        except Exception as exc:  # noqa: BLE001 — missing dialect/wheels are common
            logger.warning(
                "Turso URL set but async libsql dialect unavailable (%s); "
                "falling back to local SQLite.",
                exc,
            )

    return create_async_engine(_sqlite_url(), echo=False)


@lru_cache
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(get_engine(), expire_on_commit=False, class_=AsyncSession)


def __getattr__(name: str):
    if name == "engine":
        return get_engine()
    if name == "SessionLocal":
        return get_session_factory()
    raise AttributeError(name)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    factory = get_session_factory()
    async with factory() as session:
        yield session
