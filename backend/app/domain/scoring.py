"""Zero-sum normalization (ADR-004) and initial score state."""

from __future__ import annotations

from app.domain.types import (
    SCORE_CATEGORIES,
    SCORED_ROLES,
    CategoryScores,
    ScoreCategory,
    ScoredRole,
    TurnScores,
)


def initial_scores() -> TurnScores:
    """Turn 0 (2027-01-01) baseline from project-proposal §1.3."""
    return {
        "humanity": CategoryScores(sm=100.0, rc=100.0, ic=100.0, pc=98.0, cs=100.0),
        "rogue_ai": CategoryScores(sm=0.0, rc=0.0, ic=0.0, pc=1.0, cs=0.0),
        "defender_ai": CategoryScores(sm=0.0, rc=0.0, ic=0.0, pc=1.0, cs=0.0),
    }


def _clamp_non_negative(value: float) -> float:
    return max(0.0, value)


def normalize_category(
    raw: dict[ScoredRole, float],
) -> dict[ScoredRole, float]:
    """Rescale three seat values so they sum to exactly 100.

    Degenerate cases (all zero / all negative after clamp): equal split.
    """
    clamped = {role: _clamp_non_negative(raw.get(role, 0.0)) for role in SCORED_ROLES}
    total = sum(clamped.values())
    if total <= 0:
        equal = 100.0 / 3.0
        return {role: equal for role in SCORED_ROLES}

    scaled = {role: (clamped[role] / total) * 100.0 for role in SCORED_ROLES}
    # Fix floating-point drift on the last role so sum is exactly 100.
    others = SCORED_ROLES[0], SCORED_ROLES[1]
    scaled[SCORED_ROLES[2]] = 100.0 - scaled[others[0]] - scaled[others[1]]
    return scaled


def normalize_turn_scores(raw: TurnScores | dict[ScoredRole, dict[ScoreCategory, float]]) -> TurnScores:
    """Normalize every category independently so each sums to 100 across seats."""
    by_category: dict[ScoreCategory, dict[ScoredRole, float]] = {
        cat: {} for cat in SCORE_CATEGORIES
    }

    for role in SCORED_ROLES:
        seat = raw[role]
        values = seat.as_dict() if isinstance(seat, CategoryScores) else seat
        for cat in SCORE_CATEGORIES:
            by_category[cat][role] = float(values[cat])

    normalized_by_cat = {
        cat: normalize_category(by_category[cat]) for cat in SCORE_CATEGORIES
    }

    return {
        role: CategoryScores(
            sm=normalized_by_cat["sm"][role],
            rc=normalized_by_cat["rc"][role],
            ic=normalized_by_cat["ic"][role],
            pc=normalized_by_cat["pc"][role],
            cs=normalized_by_cat["cs"][role],
        )
        for role in SCORED_ROLES
    }


def assert_zero_sum(scores: TurnScores, *, tol: float = 1e-6) -> None:
    """Raise AssertionError if any category does not sum to ~100."""
    for cat in SCORE_CATEGORIES:
        total = sum(scores[role].as_dict()[cat] for role in SCORED_ROLES)
        if abs(total - 100.0) > tol:
            raise AssertionError(
                f"category {cat} sums to {total}, expected 100 (±{tol})"
            )
