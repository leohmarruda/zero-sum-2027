"""Replay / rewind past turns."""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_replay_rewinds_and_resolves(client):
    ac, _stub = client
    created = await ac.post("/api/games", json={})
    game_id = created.json()["id"]

    move1 = await ac.post(
        f"/api/games/{game_id}/turns/1/moves",
        json={"move_text": "First plan for January."},
    )
    assert move1.status_code == 200
    r1 = await ac.post(f"/api/games/{game_id}/turns/1/resolve")
    assert r1.status_code == 200
    assert r1.json()["game"]["current_turn"] == 2

    move2 = await ac.post(
        f"/api/games/{game_id}/turns/2/moves",
        json={"move_text": "February plan."},
    )
    assert move2.status_code == 200
    r2 = await ac.post(f"/api/games/{game_id}/turns/2/resolve")
    assert r2.status_code == 200
    assert r2.json()["game"]["current_turn"] == 3

    replay = await ac.post(
        f"/api/games/{game_id}/turns/1/replay",
        json={"move_text": "Revised January plan."},
    )
    assert replay.status_code == 200, replay.text
    body = replay.json()
    assert body["game"]["current_turn"] == 2
    assert body["turn"]["turn_number"] == 1
    human = next(m for m in body["turn"]["moves"] if m["seat_role"] == "hwg")
    assert human["move_text"] == "Revised January plan."

    # Turn 2 data must be gone until replayed again.
    t2 = await ac.get(f"/api/games/{game_id}/turns/2")
    assert t2.status_code == 200
    assert t2.json()["adjudication"] is None
    assert t2.json()["moves"] == []
