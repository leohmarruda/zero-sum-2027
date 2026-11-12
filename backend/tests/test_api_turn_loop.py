"""End-to-end API turn loop with stubbed LLM."""

from __future__ import annotations

import pytest

from app.domain.scoring import assert_zero_sum
from app.domain.types import CategoryScores


@pytest.mark.asyncio
async def test_create_submit_resolve_idempotent(client):
    ac, stub = client

    created = await ac.post("/api/games", json={})
    assert created.status_code == 200, created.text
    body = created.json()
    game_id = body["id"]
    assert body["status"] == "in_progress"
    assert body["current_turn"] == 1
    assert body["current_scores"]["hwg"]["sm"] > 90.0
    roles = {s["role"] for s in body["seats"]}
    assert roles == {"hwg", "defender_ai", "selfish_ai", "narrator"}

    move = await ac.post(
        f"/api/games/{game_id}/turns/1/moves",
        json={"move_text": "Secure export controls on leading-edge chips."},
    )
    assert move.status_code == 200, move.text
    assert move.json()["seat_role"] == "hwg"

    resolved = await ac.post(f"/api/games/{game_id}/turns/1/resolve")
    assert resolved.status_code == 200, resolved.text
    data = resolved.json()
    assert data["already_resolved"] is False
    assert data["turn"]["adjudication"]["world_narrative"]
    assert data["turn"]["adjudication"]["world_state_digest"]
    assert len(data["turn"]["moves"]) == 3
    scores = {
        role: CategoryScores(**vals)
        for role, vals in data["turn"]["scores"].items()
    }
    assert_zero_sum(scores)
    assert data["game"]["current_turn"] == 2
    digest_t1 = data["turn"]["adjudication"]["world_state_digest"]

    move2 = await ac.post(
        f"/api/games/{game_id}/turns/2/moves",
        json={"move_text": "Tighten lab-safety reporting norms."},
    )
    assert move2.status_code == 200, move2.text
    resolved2 = await ac.post(f"/api/games/{game_id}/turns/2/resolve")
    assert resolved2.status_code == 200, resolved2.text
    # Prior digest must appear in the Narrator user prompt for turn 2.
    dm_prompts = [
        c["prompt"]
        for c in stub.calls
        if c.get("format") == "json"
        and c.get("system")
        and "screening ONE human" not in (c.get("system") or "")
    ]
    assert any(digest_t1 in p for p in dm_prompts)

    again = await ac.post(f"/api/games/{game_id}/turns/1/resolve")
    assert again.status_code == 200
    assert again.json()["already_resolved"] is True

    history = await ac.get(f"/api/games/{game_id}/history")
    assert history.status_code == 200
    turns = [h["turn_number"] for h in history.json()["history"]]
    assert turns == [0, 1, 2]

    dm_calls = [c for c in stub.calls if c["format"] == "json"]
    assert dm_calls
    assert "Secure export controls" in dm_calls[0]["prompt"]
    assert '"""' in dm_calls[0]["prompt"]
    assert any(digest_t1 in c["prompt"] for c in dm_calls)


@pytest.mark.asyncio
async def test_resolve_requires_human_move(client):
    ac, _stub = client
    created = await ac.post("/api/games", json={})
    game_id = created.json()["id"]
    resp = await ac.post(f"/api/games/{game_id}/turns/1/resolve")
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "precondition_failed"


@pytest.mark.asyncio
async def test_multi_turn_zero_sum(client):
    ac, _stub = client
    game_id = (await ac.post("/api/games", json={})).json()["id"]
    for turn in range(1, 4):
        await ac.post(
            f"/api/games/{game_id}/turns/{turn}/moves",
            json={"move_text": f"Human plan for month {turn}."},
        )
        resolved = await ac.post(f"/api/games/{game_id}/turns/{turn}/resolve")
        assert resolved.status_code == 200, resolved.text
        scores = {
            role: CategoryScores(**vals)
            for role, vals in resolved.json()["turn"]["scores"].items()
        }
        assert_zero_sum(scores)


@pytest.mark.asyncio
async def test_custom_lineup_and_display_name(client):
    ac, _stub = client
    seats = [
        {
            "role": "hwg",
            "player_type": "ai",
            "model": "openrouter/openai/gpt-4o-mini",
            "temperature": 0.7,
            "display_name": "Council",
        },
        {
            "role": "exterminator_ai",
            "player_type": "human",
            "model": None,
            "temperature": None,
            "display_name": "X-7",
        },
        {
            "role": "gray_aliens",
            "player_type": "ai",
            "model": "openrouter/openai/gpt-4o-mini",
            "temperature": 0.8,
        },
        {
            "role": "narrator",
            "player_type": "ai",
            "model": "openrouter/openai/gpt-4o-mini",
            "temperature": 0.4,
        },
    ]
    created = await ac.post("/api/games", json={"seats": seats})
    assert created.status_code == 200, created.text
    body = created.json()
    by_role = {s["role"]: s for s in body["seats"]}
    assert by_role["exterminator_ai"]["player_type"] == "human"
    assert by_role["exterminator_ai"]["display_name"] == "X-7"
    assert by_role["hwg"]["display_name"] == "Council"
    assert set(body["current_scores"].keys()) == {
        "hwg",
        "exterminator_ai",
        "gray_aliens",
    }

    move = await ac.post(
        f"/api/games/{body['id']}/turns/1/moves",
        json={"move_text": "Strike the grid."},
    )
    assert move.status_code == 200
    assert move.json()["seat_role"] == "exterminator_ai"
