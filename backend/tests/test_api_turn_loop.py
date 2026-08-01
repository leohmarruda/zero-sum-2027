"""End-to-end API turn loop with stubbed LLM."""

from __future__ import annotations

import pytest

from app.domain.scoring import assert_zero_sum
from app.domain.types import CategoryScores


@pytest.mark.asyncio
async def test_create_submit_resolve_idempotent(client):
    ac, stub = client

    created = await ac.post("/games", json={})
    assert created.status_code == 200, created.text
    body = created.json()
    game_id = body["id"]
    assert body["status"] == "in_progress"
    assert body["current_turn"] == 1
    assert body["current_scores"]["humanity"]["sm"] == 100.0

    move = await ac.post(
        f"/games/{game_id}/turns/1/moves",
        json={"move_text": "Secure export controls on leading-edge chips."},
    )
    assert move.status_code == 200, move.text
    assert move.json()["seat_role"] == "humanity"

    resolved = await ac.post(f"/games/{game_id}/turns/1/resolve")
    assert resolved.status_code == 200, resolved.text
    data = resolved.json()
    assert data["already_resolved"] is False
    assert data["turn"]["adjudication"]["world_narrative"]
    assert len(data["turn"]["moves"]) == 3
    scores = {
        role: CategoryScores(**vals)
        for role, vals in data["turn"]["scores"].items()
    }
    assert_zero_sum(scores)
    assert data["game"]["current_turn"] == 2

    again = await ac.post(f"/games/{game_id}/turns/1/resolve")
    assert again.status_code == 200
    assert again.json()["already_resolved"] is True

    history = await ac.get(f"/games/{game_id}/history")
    assert history.status_code == 200
    turns = [h["turn_number"] for h in history.json()["history"]]
    assert turns == [0, 1]

    # DM prompt must quote human move, not treat as naked system text only
    dm_calls = [c for c in stub.calls if c["format"] == "json"]
    assert dm_calls
    assert "Secure export controls" in dm_calls[0]["prompt"]
    assert "quoted content" in dm_calls[0]["prompt"].lower() or "Quoted" in dm_calls[0]["prompt"] or '"""' in dm_calls[0]["prompt"]


@pytest.mark.asyncio
async def test_resolve_requires_human_move(client):
    ac, _stub = client
    created = await ac.post("/games", json={})
    game_id = created.json()["id"]
    resp = await ac.post(f"/games/{game_id}/turns/1/resolve")
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "precondition_failed"


@pytest.mark.asyncio
async def test_multi_turn_zero_sum(client):
    ac, _stub = client
    game_id = (await ac.post("/games", json={})).json()["id"]
    for turn in range(1, 4):
        await ac.post(
            f"/games/{game_id}/turns/{turn}/moves",
            json={"move_text": f"Human plan for month {turn}."},
        )
        resolved = await ac.post(f"/games/{game_id}/turns/{turn}/resolve")
        assert resolved.status_code == 200, resolved.text
        scores = {
            role: CategoryScores(**vals)
            for role, vals in resolved.json()["turn"]["scores"].items()
        }
        assert_zero_sum(scores)
