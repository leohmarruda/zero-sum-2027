"""Seeded events, score deltas, endings/containment, and prompt wiring."""

from __future__ import annotations

from app.domain.endings import (
    CONTAINMENT_WINDOW,
    classify_ending,
    containment_holds,
)
from app.domain.events import EVENT_FIRST_TURN, event_for_turn
from app.domain.transfers import score_deltas
from app.domain.types import CategoryScores, Outcome, TurnScores
from app.domain.victory import evaluate_outcome
from app.llm.prompts import (
    NARRATOR_SYSTEM_PROMPT,
    build_dm_prompt,
    build_epilogue_prompt,
    build_seat_move_prompt,
)

ROLES = ["hwg", "defender_ai", "selfish_ai"]


def _flat(value: float) -> CategoryScores:
    return CategoryScores(sm=value, rc=value, ic=value, pc=value, cs=value)


def _scores(hwg: float, dai: float, sai: float) -> TurnScores:
    return {"hwg": _flat(hwg), "defender_ai": _flat(dai), "selfish_ai": _flat(sai)}


# --- events -----------------------------------------------------------------


def test_events_are_deterministic_and_spaced():
    turns = range(1, 61)
    first = [event_for_turn("game-a", t, ROLES) for t in turns]
    again = [event_for_turn("game-a", t, ROLES) for t in turns]
    assert first == again
    fired = [t for t, e in zip(turns, first) if e is not None]
    assert fired, "expected at least one event over 60 turns"
    assert all(t >= EVENT_FIRST_TURN for t in fired)
    assert all(b - a >= 2 for a, b in zip(fired, fired[1:]))


def test_events_differ_between_games():
    a = [event_for_turn("game-a", t, ROLES) for t in range(1, 61)]
    b = [event_for_turn("game-b", t, ROLES) for t in range(1, 61)]
    assert a != b


def test_role_gated_events_need_their_seat():
    for game in (f"g{i}" for i in range(40)):
        for t in range(1, 61):
            e = event_for_turn(game, t, ROLES)
            if e is not None:
                assert not e.requires


# --- deltas -----------------------------------------------------------------


def test_score_deltas_are_zero_sum():
    before = _scores(90, 5, 5)
    after = _scores(80, 12, 8)
    deltas = score_deltas(before, after)
    assert deltas["hwg"]["pc"] == -10
    for cat in ("pc", "rc", "cs", "ic", "sm"):
        assert round(sum(d[cat] for d in deltas.values()), 6) == 0


def test_score_deltas_without_previous_is_empty():
    assert score_deltas(None, _scores(90, 5, 5)) == {}


# --- endings / containment --------------------------------------------------


def test_containment_win_for_defender_at_cap():
    history = [_scores(40, 35, 25)] * 60
    out = evaluate_outcome(turn_number=60, history=history, roles=ROLES)
    assert out.kind == Outcome.win
    assert out.winner == "defender_ai"
    assert out.ending == "containment"


def test_no_containment_when_a_seat_dominates():
    history = [_scores(70, 20, 10)] * 60
    out = evaluate_outcome(turn_number=60, history=history, roles=ROLES)
    assert out.kind == Outcome.draw
    assert out.ending == "uneasy_hegemony"


def test_containment_requires_defender_in_play():
    roles = ["hwg", "selfish_ai"]
    history = [{"hwg": _flat(50), "selfish_ai": _flat(50)}] * 60
    out = evaluate_outcome(turn_number=60, history=history, roles=roles)
    assert out.kind == Outcome.draw


def test_containment_window_must_be_full():
    assert not containment_holds([_scores(40, 35, 25)] * (CONTAINMENT_WINDOW - 1))
    assert containment_holds([_scores(40, 35, 25)] * CONTAINMENT_WINDOW)


def test_streak_win_is_hegemony():
    history = [_scores(95, 3, 2)] * 12
    out = evaluate_outcome(
        turn_number=40, history=history, roles=ROLES, humanity_win_turn=30
    )
    assert out.kind == Outcome.win and out.winner == "hwg"
    assert out.ending == "hegemony"


def test_draw_classification():
    assert classify_ending(Outcome.draw, _scores(45, 45, 10), by=None) == "bipolar_standoff"
    assert classify_ending(Outcome.draw, _scores(34, 33, 33), by=None) == "multipolar_balance"


# --- prompt wiring ----------------------------------------------------------


def test_narrator_prompt_covers_transfers_and_interdependence():
    assert "Zero-sum transfers" in NARRATOR_SYSTEM_PROMPT
    assert "Interdependence" in NARRATOR_SYSTEM_PROMPT


def test_world_event_injected_into_dm_prompt():
    scores = _scores(60, 20, 20)
    _s, user = build_dm_prompt(
        turn_number=5,
        narrative_date="2027-05-01",
        current_scores=scores,
        moves={r: "act" for r in ROLES},
        scored_roles=ROLES,
        world_event="A fab burns down.",
    )
    assert "World event this month" in user and "A fab burns down." in user
    _s, quiet = build_dm_prompt(
        turn_number=5,
        narrative_date="2027-05-01",
        current_scores=scores,
        moves={r: "act" for r in ROLES},
        scored_roles=ROLES,
    )
    assert "World event this month" not in quiet


def test_ai_seat_prompt_includes_public_world():
    _s, user = build_seat_move_prompt(
        role="selfish_ai",
        turn_number=4,
        narrative_date="2027-04-01",
        current_scores=_scores(60, 20, 20),
        prior_feedback=None,
        world_digest="Compute race is heating up.",
        public_narrative="Markets twitched.",
    )
    assert "Compute race is heating up." in user
    assert "Markets twitched." in user


def test_epilogue_prompt_mentions_ending_and_winner():
    _s, user = build_epilogue_prompt(
        ending="containment",
        winner="defender_ai",
        final_turn=60,
        history=[_scores(40, 35, 25)] * 60,
        world_state_digest="Power stayed distributed.",
    )
    assert "Containment" in user
    assert "Defender AI" in user
    assert "Turn 60" in user
