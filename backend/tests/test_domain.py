"""Unit tests for zero-sum normalization and victory evaluation."""

from app.domain.scoring import (
    assert_zero_sum,
    initial_scores,
    normalize_category,
    normalize_turn_scores,
)
from app.domain.types import CategoryScores, Outcome
from app.domain.victory import compute_streaks, evaluate_outcome


def test_initial_scores_sum_to_100():
    scores = initial_scores()
    assert_zero_sum(scores)
    assert scores["humanity"].pc == 98.0
    assert scores["rogue_ai"].pc == 1.0
    assert scores["defender_ai"].pc == 1.0


def test_normalize_category_proportional():
    raw = {"rogue_ai": 50.0, "defender_ai": 30.0, "humanity": 40.0}  # sum 120
    out = normalize_category(raw)
    assert abs(sum(out.values()) - 100.0) < 1e-9
    assert abs(out["rogue_ai"] - (50 / 120) * 100) < 1e-9


def test_normalize_category_all_zero_equal_split():
    out = normalize_category({"rogue_ai": 0.0, "defender_ai": 0.0, "humanity": 0.0})
    assert abs(sum(out.values()) - 100.0) < 1e-9
    for v in out.values():
        assert abs(v - 100.0 / 3.0) < 1e-9


def test_normalize_category_clamps_negatives():
    out = normalize_category({"rogue_ai": -10.0, "defender_ai": 50.0, "humanity": 50.0})
    assert out["rogue_ai"] == 0.0
    assert abs(sum(out.values()) - 100.0) < 1e-9


def test_normalize_turn_scores():
    raw = {
        "rogue_ai": CategoryScores(sm=200, rc=0, ic=0, pc=0, cs=0),
        "defender_ai": CategoryScores(sm=100, rc=0, ic=0, pc=0, cs=0),
        "humanity": CategoryScores(sm=100, rc=100, ic=100, pc=100, cs=100),
    }
    out = normalize_turn_scores(raw)
    assert_zero_sum(out)
    # sm: 200/400, 100/400, 100/400
    assert abs(out["rogue_ai"].sm - 50.0) < 1e-9


def _high(role_focus: str) -> CategoryScores:
    """Near-max composite for one seat; remainder split so categories sum to 100."""
    high = 96.0
    low = 2.0
    mapping = {
        "rogue_ai": (high, low, low),
        "defender_ai": (low, high, low),
        "humanity": (low, low, high),
    }
    r, d, h = mapping[role_focus]
    return {
        "rogue_ai": CategoryScores(sm=r, rc=r, ic=r, pc=r, cs=r),
        "defender_ai": CategoryScores(sm=d, rc=d, ic=d, pc=d, cs=d),
        "humanity": CategoryScores(sm=h, rc=h, ic=h, pc=h, cs=h),
    }


def test_composite_threshold():
    scores = _high("rogue_ai")
    assert scores["rogue_ai"].composite() >= 0.9
    assert scores["humanity"].composite() < 0.9


def test_streak_and_rogue_win():
    history = [_high("rogue_ai") for _ in range(10)]
    streaks = compute_streaks(history)
    assert streaks["rogue_ai"] == 10
    outcome = evaluate_outcome(turn_number=10, history=history)
    assert outcome.kind == Outcome.win
    assert outcome.winner == "rogue_ai"


def test_humanity_cannot_win_before_turn_30():
    history = [_high("humanity") for _ in range(10)]
    outcome = evaluate_outcome(turn_number=20, history=history)
    assert outcome.kind == Outcome.continue_
    outcome_late = evaluate_outcome(turn_number=30, history=history)
    assert outcome_late.kind == Outcome.win
    assert outcome_late.winner == "humanity"


def test_draw_at_turn_cap():
    low = {
        "rogue_ai": CategoryScores(sm=33, rc=33, ic=34, pc=33, cs=33),
        "defender_ai": CategoryScores(sm=33, rc=34, ic=33, pc=33, cs=34),
        "humanity": CategoryScores(sm=34, rc=33, ic=33, pc=34, cs=33),
    }
    # Fix to exact zero-sum via normalize
    from app.domain.scoring import normalize_turn_scores

    mid = normalize_turn_scores(low)
    history = [mid] * 60
    outcome = evaluate_outcome(turn_number=60, history=history)
    assert outcome.kind == Outcome.draw
    assert outcome.winner is None


def test_streak_resets_on_break():
    high = _high("rogue_ai")
    mid = normalize_turn_scores(
        {
            "rogue_ai": CategoryScores(sm=20, rc=20, ic=20, pc=20, cs=20),
            "defender_ai": CategoryScores(sm=40, rc=40, ic=40, pc=40, cs=40),
            "humanity": CategoryScores(sm=40, rc=40, ic=40, pc=40, cs=40),
        }
    )
    history = [high, high, mid, high, high]
    assert compute_streaks(history)["rogue_ai"] == 2
