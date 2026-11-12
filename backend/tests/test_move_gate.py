"""Human move plausibility gate — reject returns the turn to the player."""

from __future__ import annotations

import pytest

from app.domain.scoring import initial_scores
from app.llm.prompts import build_move_gate_prompt


def test_move_gate_prompt_quotes_move():
    system, user = build_move_gate_prompt(
        role="hwg",
        turn_number=1,
        narrative_date="2027-01-01",
        current_scores=initial_scores(("hwg", "defender_ai", "selfish_ai")),
        move_text="Eliminate every other faction this month.",
    )
    assert "screening ONE human" in system
    assert "Eliminate every other faction" in user
    assert '"""' in user
    assert "accepted" in user


@pytest.mark.asyncio
async def test_resolve_rejects_implausible_human_move(client):
    ac, stub = client
    stub.reject_next_move = True

    created = await ac.post("/api/games", json={})
    assert created.status_code == 200
    game_id = created.json()["id"]

    move = await ac.post(
        f"/api/games/{game_id}/turns/1/moves",
        json={"move_text": "Wipe out all other players instantly."},
    )
    assert move.status_code == 200

    resolved = await ac.post(f"/api/games/{game_id}/turns/1/resolve")
    assert resolved.status_code == 200
    body = resolved.json()
    assert body["rejected"] is True
    assert body["rejection_reason"]
    assert body["game"]["current_turn"] == 1
    assert body["turn"]["adjudication"] is None

    # Human move cleared — can submit again.
    again = await ac.post(
        f"/api/games/{game_id}/turns/1/moves",
        json={"move_text": "Secure critical fabs and coordinate with Defender AI."},
    )
    assert again.status_code == 200

    ok = await ac.post(f"/api/games/{game_id}/turns/1/resolve")
    assert ok.status_code == 200
    ok_body = ok.json()
    assert ok_body["rejected"] is False
    assert ok_body["game"]["current_turn"] == 2
    assert ok_body["turn"]["adjudication"] is not None
