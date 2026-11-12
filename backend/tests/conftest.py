"""Shared fixtures for API/integration tests."""

from __future__ import annotations

import json

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db import Base, get_session
from app.llm.types import LLMOutput
from app.main import app

DEFAULT_ROLES = ("hwg", "defender_ai", "selfish_ai")


class StubLLM:
    """Deterministic LLM stub: seat moves are plain text; Narrator returns JSON scores."""

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
        self.calls.append(
            {"model": model, "prompt": prompt, "system": system, "format": response_format}
        )
        if system and "screening ONE human" in (system or ""):
            if getattr(self, "reject_next_move", False):
                self.reject_next_move = False
                return LLMOutput(
                    content=json.dumps(
                        {
                            "accepted": False,
                            "reason": "That one-month wipeout is not plausible.",
                        }
                    ),
                    model=model,
                )
            return LLMOutput(
                content=json.dumps({"accepted": True, "reason": ""}),
                model=model,
            )
        if system and "closing EPILOGUE" in system:
            return LLMOutput(content="Epilogue: the balance held.", model=model)
        if response_format == "json" or (system and "Narrator" in (system or "") and "/off" not in (system or "")):
            s = self.score_shift
            payload = {
                "world_narrative": "Markets twitched; compute bids rose.",
                "world_state_digest": (
                    "Compute race multipolar; markets twitch; no biosphere threat."
                ),
                "seat_feedback": {
                    "selfish_ai": "Your probe succeeded modestly.",
                    "defender_ai": "You contained the worst of it.",
                    "hwg": "You held most levers.",
                },
                "scores": {
                    "selfish_ai": {"sm": s, "rc": s, "ic": s, "pc": 1 + s, "cs": s},
                    "defender_ai": {"sm": s, "rc": s, "ic": s, "pc": 1 + s, "cs": s},
                    "hwg": {
                        "sm": 100 - 2 * s,
                        "rc": 100 - 2 * s,
                        "ic": 100 - 2 * s,
                        "pc": 98 - 2 * s,
                        "cs": 100 - 2 * s,
                    },
                },
            }
            return LLMOutput(content=json.dumps(payload), model=model)
        if system and "/off" in system:
            return LLMOutput(
                content=(
                    "That is public knowledge in January 2027: AGI has been reached. "
                    "I will not disclose other seats' private plans."
                ),
                model=model,
            )
        role = "ai"
        if system:
            if "Selfish" in system:
                role = "selfish"
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
