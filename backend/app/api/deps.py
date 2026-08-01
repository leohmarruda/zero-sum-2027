"""FastAPI dependency wiring."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.llm.client import LlmCallClient
from app.llm.types import LLMClient
from app.services.game_service import GameService
from app.services.turn_service import TurnService


def get_llm(request: Request) -> LLMClient:
    override = getattr(request.app.state, "llm_client", None)
    if override is not None:
        return override
    return LlmCallClient()


async def get_game_service(
    session: AsyncSession = Depends(get_session),
) -> AsyncGenerator[GameService, None]:
    yield GameService(session)


async def get_turn_service(
    session: AsyncSession = Depends(get_session),
    llm: LLMClient = Depends(get_llm),
) -> AsyncGenerator[TurnService, None]:
    yield TurnService(session, llm)
