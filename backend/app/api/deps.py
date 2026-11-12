"""FastAPI dependency wiring."""

from __future__ import annotations

from collections.abc import AsyncGenerator, Mapping

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.llm.client import API_KEY_PROVIDERS, LlmCallClient
from app.llm.types import LLMClient
from app.services.game_service import GameService
from app.services.turn_service import TurnService


_KEY_HEADER_PREFIX = "x-api-key-"
_MAX_KEY_LEN = 512


def api_keys_from_headers(headers: Mapping[str, str]) -> dict[str, str]:
    """Per-request provider keys from `X-Api-Key-<provider>` headers.

    Only known providers are accepted. Values are never logged or stored.
    """
    keys: dict[str, str] = {}
    for name, value in headers.items():
        lowered = name.lower()
        if not lowered.startswith(_KEY_HEADER_PREFIX):
            continue
        provider = lowered[len(_KEY_HEADER_PREFIX) :]
        key = value.strip()
        if provider in API_KEY_PROVIDERS and key and len(key) <= _MAX_KEY_LEN:
            keys[provider] = key
    return keys


def get_llm(request: Request) -> LLMClient:
    override = getattr(request.app.state, "llm_client", None)
    if override is not None:
        return override
    return LlmCallClient(api_keys=api_keys_from_headers(request.headers))


async def get_game_service(
    session: AsyncSession = Depends(get_session),
) -> AsyncGenerator[GameService, None]:
    yield GameService(session)


async def get_turn_service(
    session: AsyncSession = Depends(get_session),
    llm: LLMClient = Depends(get_llm),
) -> AsyncGenerator[TurnService, None]:
    yield TurnService(session, llm)
