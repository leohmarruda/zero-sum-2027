"""Full-game simulation: turn 1 → win or draw, zero-sum every turn."""

from __future__ import annotations

import json

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db import Base, get_session
from app.domain.scoring import assert_zero_sum
from app.domain.types import CategoryScores
from app.llm.types import LLMOutput
from app.main import app


class ScriptedDMStub:
    """Seat moves are filler; DM scores come from `score_fn(turn) -> dict`."""

    def __init__(self, score_fn):
        self.score_fn = score_fn
        self.resolve_count = 0

    async def complete(self, model, prompt, *, system=None, response_format="text", **kwargs):
        if response_format == "json" or (system and "Dungeon Master" in (system or "")):
            self.resolve_count += 1
            scores = self.score_fn(self.resolve_count)
            payload = {
                "world_narrative": f"Month {self.resolve_count}: the board shifts.",
                "seat_feedback": {
                    "rogue_ai": "Noted.",
                    "defender_ai": "Noted.",
                    "humanity": "Noted.",
                },
                "scores": scores,
            }
            return LLMOutput(content=json.dumps(payload), model=model)
        return LLMOutput(content="AI acts this month.", model=model)


def _shares(rogue: float, defender: float, humanity: float) -> dict:
    """Uniform category shares (already sum to 100)."""
    assert abs(rogue + defender + humanity - 100.0) < 1e-6
    return {
        "rogue_ai": {"sm": rogue, "rc": rogue, "ic": rogue, "pc": rogue, "cs": rogue},
        "defender_ai": {
            "sm": defender,
            "rc": defender,
            "ic": defender,
            "pc": defender,
            "cs": defender,
        },
        "humanity": {
            "sm": humanity,
            "rc": humanity,
            "ic": humanity,
            "pc": humanity,
            "cs": humanity,
        },
    }


@pytest_asyncio.fixture
async def api_with_stub():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    session_factory = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    holders: dict = {"stub": None}

    async def _override_session():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = _override_session
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:

        def install(stub):
            holders["stub"] = stub
            app.state.llm_client = stub
            return ac

        yield install

    app.dependency_overrides.clear()
    if hasattr(app.state, "llm_client"):
        delattr(app.state, "llm_client")
    await engine.dispose()


async def _play_until_ended(ac: AsyncClient, max_turns: int = 60) -> dict:
    created = await ac.post("/api/games", json={})
    assert created.status_code == 200, created.text
    game_id = created.json()["id"]
    last = None
    for turn in range(1, max_turns + 1):
        move = await ac.post(
            f"/api/games/{game_id}/turns/{turn}/moves",
            json={"move_text": f"Humanity plan for turn {turn}."},
        )
        assert move.status_code == 200, move.text
        resolved = await ac.post(f"/api/games/{game_id}/turns/{turn}/resolve")
        assert resolved.status_code == 200, resolved.text
        last = resolved.json()
        scores = {
            role: CategoryScores(**vals)
            for role, vals in last["turn"]["scores"].items()
        }
        assert_zero_sum(scores)
        if last["game"]["status"] == "ended":
            return {
                "game_id": game_id,
                "ended_on_turn": turn,
                "winner": last["game"]["winner"],
                "final": last,
            }
        assert last["game"]["current_turn"] == turn + 1
    raise AssertionError("game did not end within max_turns")


@pytest.mark.asyncio
async def test_full_game_rogue_wins_on_streak(api_with_stub):
    # Rogue at 96% composite for 10 consecutive turns → win at turn 10.
    stub = ScriptedDMStub(lambda _t: _shares(96.0, 2.0, 2.0))
    ac = api_with_stub(stub)
    result = await _play_until_ended(ac, max_turns=15)
    assert result["ended_on_turn"] == 10
    assert result["winner"] == "rogue_ai"
    assert result["final"]["game"]["status"] == "ended"


@pytest.mark.asyncio
async def test_full_game_draw_at_turn_cap(api_with_stub):
    # Nobody reaches ≥0.9; game draws at turn 60.
    stub = ScriptedDMStub(lambda _t: _shares(34.0, 33.0, 33.0))
    ac = api_with_stub(stub)
    result = await _play_until_ended(ac, max_turns=60)
    assert result["ended_on_turn"] == 60
    assert result["winner"] is None
    assert result["final"]["game"]["status"] == "ended"

    history = await ac.get(f"/api/games/{result['game_id']}/history")
    assert history.status_code == 200
    turns = [h["turn_number"] for h in history.json()["history"]]
    assert turns[0] == 0
    assert turns[-1] == 60
    assert len(turns) == 61
    for point in history.json()["history"]:
        scores = {
            role: CategoryScores(**vals) for role, vals in point["scores"].items()
        }
        assert_zero_sum(scores)


@pytest.mark.asyncio
async def test_humanity_cannot_win_before_turn_30_even_with_streak(api_with_stub):
    stub = ScriptedDMStub(lambda _t: _shares(2.0, 2.0, 96.0))
    ac = api_with_stub(stub)
    created = await ac.post("/api/games", json={})
    game_id = created.json()["id"]
    for turn in range(1, 12):
        await ac.post(
            f"/api/games/{game_id}/turns/{turn}/moves",
            json={"move_text": "Push for dominance."},
        )
        resolved = await ac.post(f"/api/games/{game_id}/turns/{turn}/resolve")
        body = resolved.json()
        scores = {
            role: CategoryScores(**vals)
            for role, vals in body["turn"]["scores"].items()
        }
        assert_zero_sum(scores)
        assert body["game"]["status"] == "in_progress"
        assert body["game"]["winner"] is None
