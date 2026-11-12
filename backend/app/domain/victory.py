"""Win streak and end-of-game evaluation."""

from __future__ import annotations

from collections.abc import Sequence

from app.domain.endings import classify_ending, containment_holds
from app.domain.roles import DELAYED_WIN_ROLES, SeatRole
from app.domain.types import (
    HUMANITY_WIN_TURN,
    WIN_STREAK_REQUIRED,
    GameOutcome,
    Outcome,
    ScoredRole,
    TurnScores,
    win_threshold,
)


def composite_meets_threshold(
    scores: TurnScores, role: ScoredRole, *, threshold: float
) -> bool:
    return scores[role].composite() >= threshold


def compute_streaks(
    history: list[TurnScores],
    roles: Sequence[ScoredRole],
) -> dict[ScoredRole, int]:
    """Trailing consecutive turns at-or-above threshold, per scored seat.

    `history` is ordered oldest→newest and should exclude turn 0 if turn 0
    is only the setup baseline (streaks count resolved play turns).
    Threshold is 0.85 + 0.15/N for N = len(roles) (narrator excluded).
    """
    roles = list(roles)
    streaks: dict[ScoredRole, int] = {role: 0 for role in roles}
    if not history:
        return streaks

    threshold = win_threshold(len(roles))
    for role in roles:
        count = 0
        for scores in reversed(history):
            if role not in scores:
                break
            if composite_meets_threshold(scores, role, threshold=threshold):
                count += 1
            else:
                break
        streaks[role] = count
    return streaks


def evaluate_outcome(
    *,
    turn_number: int,
    history: list[TurnScores],
    roles: Sequence[ScoredRole],
    turn_cap: int = 60,
    humanity_win_turn: int = HUMANITY_WIN_TURN,
) -> GameOutcome:
    """Evaluate after a turn has been resolved and appended to history.

    Delayed-win polities (HWG/US/China/EU) may only win from `humanity_win_turn`
    onward. If multiple seats hit streak simultaneously, priority follows
    the `roles` order passed in (stable, documented).
    """
    roles = list(roles)
    streaks = compute_streaks(history, roles)
    final: TurnScores = history[-1] if history else {}

    for role in roles:
        if streaks[role] < WIN_STREAK_REQUIRED:
            continue
        try:
            seat_role = SeatRole(role)
        except ValueError:
            seat_role = None
        if seat_role in DELAYED_WIN_ROLES and turn_number < humanity_win_turn:
            continue
        return GameOutcome(
            kind=Outcome.win,
            winner=role,
            ending=classify_ending(Outcome.win, final, by="streak"),
        )

    if turn_number >= turn_cap:
        # Faction victory: Defender AI wins by containment if no seat dominated
        # during the final window. Otherwise the cap is a draw, classified by shape.
        if SeatRole.defender_ai.value in roles and containment_holds(history):
            return GameOutcome(
                kind=Outcome.win,
                winner=SeatRole.defender_ai.value,
                ending=classify_ending(Outcome.win, final, by="containment"),
            )
        return GameOutcome(
            kind=Outcome.draw,
            ending=classify_ending(Outcome.draw, final, by=None),
        )

    return GameOutcome(kind=Outcome.continue_)
