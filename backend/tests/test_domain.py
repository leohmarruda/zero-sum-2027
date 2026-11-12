"""Domain unit tests — zero-sum normalize + victory streaks."""

from __future__ import annotations

from app.domain.scoring import (
    assert_zero_sum,
    initial_scores,
    normalize_category,
    normalize_turn_scores,
)
from app.domain.types import CategoryScores, Outcome, win_threshold
from app.domain.victory import compute_streaks, evaluate_outcome

ROLES = ("hwg", "defender_ai", "selfish_ai")


def test_initial_scores_hwg_dominant():
    scores = initial_scores(ROLES)
    assert_zero_sum(scores, ROLES)
    assert scores["hwg"].pc == normalize_turn_scores(
        {
            "hwg": CategoryScores(sm=100, rc=100, ic=100, pc=98, cs=100),
            "defender_ai": CategoryScores(sm=0, rc=0, ic=0, pc=1, cs=0),
            "selfish_ai": CategoryScores(sm=0, rc=0, ic=0, pc=1, cs=0),
        },
        ROLES,
    )["hwg"].pc


def test_normalize_category_scales_to_100():
    raw = {"selfish_ai": 50.0, "defender_ai": 30.0, "hwg": 40.0}  # sum 120
    out = normalize_category(raw, ROLES)
    assert abs(sum(out.values()) - 100.0) < 1e-9
    assert abs(out["selfish_ai"] - (50 / 120) * 100) < 1e-9


def test_normalize_category_all_zero_equal_split():
    out = normalize_category(
        {"selfish_ai": 0.0, "defender_ai": 0.0, "hwg": 0.0}, ROLES
    )
    assert abs(out["hwg"] - 100.0 / 3) < 1e-9


def test_normalize_category_clamps_negatives():
    out = normalize_category(
        {"selfish_ai": -10.0, "defender_ai": 50.0, "hwg": 50.0}, ROLES
    )
    assert out["selfish_ai"] == 0.0
    assert abs(sum(out.values()) - 100.0) < 1e-9


def test_normalize_turn_scores_per_category():
    raw = {
        "selfish_ai": CategoryScores(sm=200, rc=0, ic=0, pc=0, cs=0),
        "defender_ai": CategoryScores(sm=100, rc=0, ic=0, pc=0, cs=0),
        "hwg": CategoryScores(sm=100, rc=100, ic=100, pc=100, cs=100),
    }
    out = normalize_turn_scores(raw, ROLES)
    assert_zero_sum(out, ROLES)
    assert abs(out["selfish_ai"].sm - 50.0) < 1e-9


def _high(winner: str) -> dict:
    high, low = 96.0, 2.0
    values = {role: (high if role == winner else low) for role in ROLES}
    return {
        role: CategoryScores(
            sm=values[role],
            rc=values[role],
            ic=values[role],
            pc=values[role],
            cs=values[role],
        )
        for role in ROLES
    }


def test_win_threshold_scales_with_n():
    assert abs(win_threshold(1) - 1.0) < 1e-12
    assert abs(win_threshold(3) - 0.9) < 1e-12
    assert abs(win_threshold(5) - (0.85 + 0.15 / 5)) < 1e-12


def test_composite_threshold():
    threshold = win_threshold(len(ROLES))
    scores = _high("selfish_ai")
    assert scores["selfish_ai"].composite() >= threshold
    assert scores["hwg"].composite() < threshold


def test_rogue_style_win_after_10():
    history = [_high("selfish_ai") for _ in range(10)]
    streaks = compute_streaks(history, ROLES)
    assert streaks["selfish_ai"] == 10
    outcome = evaluate_outcome(turn_number=10, history=history, roles=ROLES)
    assert outcome.kind == Outcome.win
    assert outcome.winner == "selfish_ai"


def test_hwg_cannot_win_before_turn_30():
    history = [_high("hwg") for _ in range(10)]
    early = evaluate_outcome(turn_number=11, history=history, roles=ROLES)
    assert early.kind == Outcome.continue_
    late = evaluate_outcome(turn_number=30, history=history, roles=ROLES)
    assert late.kind == Outcome.win
    assert late.winner == "hwg"


def test_draw_at_cap():
    # One seat dominates (0.70) without a decisive streak: draw, no containment.
    lead = {
        "selfish_ai": CategoryScores(sm=70, rc=70, ic=70, pc=70, cs=70),
        "defender_ai": CategoryScores(sm=15, rc=15, ic=15, pc=15, cs=15),
        "hwg": CategoryScores(sm=15, rc=15, ic=15, pc=15, cs=15),
    }
    history = [lead] * 60
    outcome = evaluate_outcome(turn_number=60, history=history, roles=ROLES)
    assert outcome.kind == Outcome.draw
    assert outcome.ending == "uneasy_hegemony"


def test_balanced_cap_is_defender_containment_win():
    mid = {
        "selfish_ai": CategoryScores(sm=33, rc=33, ic=34, pc=33, cs=33),
        "defender_ai": CategoryScores(sm=33, rc=34, ic=33, pc=33, cs=34),
        "hwg": CategoryScores(sm=34, rc=33, ic=33, pc=34, cs=33),
    }
    outcome = evaluate_outcome(turn_number=60, history=[mid] * 60, roles=ROLES)
    assert outcome.kind == Outcome.win
    assert outcome.winner == "defender_ai"
    assert outcome.ending == "containment"


def test_streak_breaks():
    high = _high("selfish_ai")
    broken = {
        "selfish_ai": CategoryScores(sm=20, rc=20, ic=20, pc=20, cs=20),
        "defender_ai": CategoryScores(sm=40, rc=40, ic=40, pc=40, cs=40),
        "hwg": CategoryScores(sm=40, rc=40, ic=40, pc=40, cs=40),
    }
    history = [high, high, broken, high, high]
    assert compute_streaks(history, ROLES)["selfish_ai"] == 2
