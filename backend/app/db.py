"""SQLAlchemy async engine and session factory."""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings


class Base(DeclarativeBase):
    pass


def _database_url() -> str:
    settings = get_settings()
    # Vercel serverless FS is ephemeral; persist only under /tmp unless Turso is set.
    if os.environ.get("VERCEL") and not (
        settings.environment == "prod" and settings.turso_database_url
    ):
        return "sqlite+aiosqlite:////tmp/zero-sum.db"
    if settings.environment == "prod" and settings.turso_database_url:
        return settings.turso_database_url
    return settings.database_url


engine = create_async_engine(_database_url(), echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
