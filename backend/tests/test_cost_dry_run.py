"""Gate A assumption #4 — dry_run cost estimate for a full game."""

from __future__ import annotations

import pytest

pytest.importorskip("llmcall")

from scripts.estimate_game_cost import estimate_full_game


def test_dry_run_cost_estimate_60_turns():
    report = estimate_full_game(turns=60)
    assert report["total_calls"] == 180  # 60 * (2 seats + 1 DM)
    assert report["estimated_cost_usd_full_game"] > 0
    # Sanity: Lite prototype should stay cheap on gpt-4o-mini class models.
    assert report["estimated_cost_usd_full_game"] < 5.0
    print("\nCOST_REPORT", report)
