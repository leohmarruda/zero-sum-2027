"""Per-turn score deltas — who gained and who lost between two snapshots."""

from __future__ import annotations

from app.domain.types import SCORE_CATEGORIES, TurnScores

# role -> category -> signed change in absolute share points
ScoreDeltas = dict[str, dict[str, float]]


def score_deltas(previous: TurnScores | None, current: TurnScores) -> ScoreDeltas:
    """Signed per-category change for every seat in `current`.

    Seats missing from `previous` are treated as 0. With no previous snapshot,
    returns an empty dict (nothing to compare against).
    """
    if previous is None:
        return {}
    out: ScoreDeltas = {}
    for role, cats in current.items():
        before = previous.get(role)
        out[role] = {
            cat: round(getattr(cats, cat) - (getattr(before, cat) if before else 0.0), 2)
            for cat in SCORE_CATEGORIES
        }
    return out
