"""Shared fixtures for API/integration tests."""

from __future__ import annotations

import json

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db import Base, get_session
from app.llm.types import LLMOutput
from app.main import app


class StubLLM:
    """Deterministic LLM stub: seat moves are plain text; DM returns JSON scores."""

    def __init__(self, score_shift: float = 2.0):
        self.score_shift = score_shift
        self.calls: list[dict] = []

    async def complete(
        self,
        model: str,
        prompt: str,
        *,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        response_format: str = "text",
        timeout_seconds: float = 60.0,
        dry_run: bool = False,
    ) -> LLMOutput:
        self.calls.append({"model": model, "prompt": prompt, "system": system, "format": response_format})
        if response_format == "json" or (system and "Dungeon Master" in system):
            # Shift a little power from humanity toward rogue each resolve.
            s = self.score_shift
            payload = {
                "world_narrative": "Markets twitched; compute bids rose.",
                "seat_feedback": {
                    "rogue_ai": "Your probe succeeded modestly.",
                    "defender_ai": "You contained the worst of it.",
                    "humanity": "You held most levers.",
                },
                "scores": {
                    "rogue_ai": {"sm": s, "rc": s, "ic": s, "pc": 1 + s, "cs": s},
                    "defender_ai": {"sm": s, "rc": s, "ic": s, "pc": 1 + s, "cs": s},
                    "humanity": {
                        "sm": 100 - 2 * s,
                        "rc": 100 - 2 * s,
                        "ic": 100 - 2 * s,
                        "pc": 98 - 2 * s,
                        "cs": 100 - 2 * s,
                    },
                },
            }
            return LLMOutput(content=json.dumps(payload), model=model)
        # Seat move
        role = "ai"
        if system:
            if "Rogue" in system:
                role = "rogue"
            elif "Defender" in system:
                role = "defender"
        return LLMOutput(content=f"{role} acts cautiously this month.", model=model)


@pytest_asyncio.fixture
async def client():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    stub = StubLLM()
    app.state.llm_client = stub

    async def _override_session():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = _override_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac, stub

    app.dependency_overrides.clear()
    if hasattr(app.state, "llm_client"):
        delattr(app.state, "llm_client")
    await engine.dispose()
