"""Zero-sum normalization (ADR-004) and initial score state."""

from __future__ import annotations

from collections.abc import Sequence

from app.domain.types import (
    SCORE_CATEGORIES,
    CategoryScores,
    ScoreCategory,
    ScoredRole,
    TurnScores,
)


def initial_scores(roles: Sequence[ScoredRole]) -> TurnScores:
    """Turn 0 baseline. HWG (if present) starts near-total control; else equal split."""
    roles = list(roles)
    if not roles:
        raise ValueError("at least one scored role required")

    if "hwg" in roles:
        raw: TurnScores = {}
        for role in roles:
            if role == "hwg":
                raw[role] = CategoryScores(sm=100.0, rc=100.0, ic=100.0, pc=98.0, cs=100.0)
            else:
                raw[role] = CategoryScores(sm=0.0, rc=0.0, ic=0.0, pc=1.0, cs=0.0)
        return normalize_turn_scores(raw, roles)

    equal = 100.0 / len(roles)
    return {
        role: CategoryScores(sm=equal, rc=equal, ic=equal, pc=equal, cs=equal)
        for role in roles
    }


def _clamp_non_negative(value: float) -> float:
    return max(0.0, value)


def normalize_category(
    raw: dict[ScoredRole, float],
    roles: Sequence[ScoredRole],
) -> dict[ScoredRole, float]:
    """Rescale seat values so they sum to exactly 100.

    Degenerate cases (all zero / all negative after clamp): equal split.
    """
    roles = list(roles)
    clamped = {role: _clamp_non_negative(raw.get(role, 0.0)) for role in roles}
    total = sum(clamped.values())
    if total <= 0:
        equal = 100.0 / len(roles)
        return {role: equal for role in roles}

    scaled = {role: (clamped[role] / total) * 100.0 for role in roles}
    # Fix floating-point drift on the last role so sum is exactly 100.
    head = roles[:-1]
    last = roles[-1]
    scaled[last] = 100.0 - sum(scaled[r] for r in head)
    return scaled


def normalize_turn_scores(
    raw: TurnScores | dict[ScoredRole, dict[ScoreCategory, float]],
    roles: Sequence[ScoredRole] | None = None,
) -> TurnScores:
    """Normalize every category independently so each sums to 100 across seats."""
    if roles is None:
        roles = list(raw.keys())
    roles = list(roles)

    by_category: dict[ScoreCategory, dict[ScoredRole, float]] = {
        cat: {} for cat in SCORE_CATEGORIES
    }

    for role in roles:
        seat = raw[role]
        values = seat.as_dict() if isinstance(seat, CategoryScores) else seat
        for cat in SCORE_CATEGORIES:
            by_category[cat][role] = float(values[cat])

    normalized_by_cat = {
        cat: normalize_category(by_category[cat], roles) for cat in SCORE_CATEGORIES
    }

    return {
        role: CategoryScores(
            sm=normalized_by_cat["sm"][role],
            rc=normalized_by_cat["rc"][role],
            ic=normalized_by_cat["ic"][role],
            pc=normalized_by_cat["pc"][role],
            cs=normalized_by_cat["cs"][role],
        )
        for role in roles
    }


def assert_zero_sum(
    scores: TurnScores,
    roles: Sequence[ScoredRole] | None = None,
    *,
    tol: float = 1e-6,
) -> None:
    """Raise AssertionError if any category does not sum to ~100."""
    roles = list(roles) if roles is not None else list(scores.keys())
    for cat in SCORE_CATEGORIES:
        total = sum(scores[role].as_dict()[cat] for role in roles)
        if abs(total - 100.0) > tol:
            raise AssertionError(
                f"category {cat} sums to {total}, expected 100 (±{tol})"
            )
