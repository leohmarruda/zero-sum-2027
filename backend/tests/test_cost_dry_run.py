"""Gate A assumption #4 — dry_run cost estimate for a full game."""

from __future__ import annotations

import pytest

pytest.importorskip("llmcall")

from scripts.estimate_game_cost import (
    _quadratic_game_cost_from_per_turn_samples,
    estimate_full_game,
)


def test_dry_run_cost_estimate_60_turns():
    report = estimate_full_game(turns=60)
    assert report["total_calls"] == 180  # 60 * (2 seats + 1 DM)
    assert report["estimated_cost_usd_full_game"] > 0
    # Sanity: Lite prototype should stay cheap on gpt-4o-mini class models.
    assert report["estimated_cost_usd_full_game"] < 5.0
    print("\nCOST_REPORT", report)


def test_quadratic_interpolate_grows_with_linear_per_turn_cost():
    """If cost/turn rises linearly, sum over T turns is ~O(T²), not T×c1."""
    flat = _quadratic_game_cost_from_per_turn_samples(
        cost_at_turn={1: 1.0, 55: 1.0}, turns=60
    )
    growing = _quadratic_game_cost_from_per_turn_samples(
        cost_at_turn={1: 1.0, 55: 3.0}, turns=60
    )
    assert flat == pytest.approx(60.0)
    assert growing > flat
    # Midpoint-ish: average cost ~2.0 over most of the arc → well above 60.
    assert growing > 100.0
