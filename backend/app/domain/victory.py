"""Win streak and end-of-game evaluation."""

from __future__ import annotations

from app.domain.types import (
    HUMANITY_WIN_TURN,
    SCORED_ROLES,
    WIN_STREAK_REQUIRED,
    WIN_THRESHOLD,
    GameOutcome,
    Outcome,
    ScoredRole,
    TurnScores,
)


def composite_meets_threshold(scores: TurnScores, role: ScoredRole) -> bool:
    return scores[role].composite() >= WIN_THRESHOLD


def compute_streaks(
    history: list[TurnScores],
) -> dict[ScoredRole, int]:
    """Trailing consecutive turns at-or-above threshold, per scored seat.

    `history` is ordered oldest→newest and should exclude turn 0 if turn 0
    is only the setup baseline (streaks count resolved play turns).
    """
    streaks: dict[ScoredRole, int] = {role: 0 for role in SCORED_ROLES}
    if not history:
        return streaks

    for role in SCORED_ROLES:
        count = 0
        for scores in reversed(history):
            if composite_meets_threshold(scores, role):
                count += 1
            else:
                break
        streaks[role] = count
    return streaks


def evaluate_outcome(
    *,
    turn_number: int,
    history: list[TurnScores],
    turn_cap: int = 60,
    humanity_win_turn: int = HUMANITY_WIN_TURN,
) -> GameOutcome:
    """Evaluate after a turn has been resolved and appended to history.

    Humanity may only win from `humanity_win_turn` onward.
    If multiple seats hit streak simultaneously, priority is
    rogue_ai → defender_ai → humanity (stable, documented order).
    """
    streaks = compute_streaks(history)

    for role in SCORED_ROLES:
        if streaks[role] < WIN_STREAK_REQUIRED:
            continue
        if role == "humanity" and turn_number < humanity_win_turn:
            continue
        return GameOutcome(kind=Outcome.win, winner=role)

    if turn_number >= turn_cap:
        return GameOutcome(kind=Outcome.draw)

    return GameOutcome(kind=Outcome.continue_)
