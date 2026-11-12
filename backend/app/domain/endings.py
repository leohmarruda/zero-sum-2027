"""Ending classification and faction-specific victory conditions."""

from __future__ import annotations

from collections.abc import Sequence

from app.domain.types import WIN_STREAK_REQUIRED, Outcome, TurnScores

ENDING_HEGEMONY = "hegemony"  # a seat held the win threshold for the full streak
ENDING_CONTAINMENT = "containment"  # Defender AI kept power distributed to the cap
ENDING_UNEASY_HEGEMONY = "uneasy_hegemony"  # one seat dominates, no decisive win
ENDING_BIPOLAR = "bipolar_standoff"
ENDING_MULTIPOLAR = "multipolar_balance"

# Containment (Defender AI win at the turn cap): no seat's composite may exceed
# this ceiling in any of the final WIN_STREAK_REQUIRED turns.
CONTAINMENT_CEILING = 0.60
CONTAINMENT_WINDOW = WIN_STREAK_REQUIRED

# Draw classification thresholds on final composites (they sum to 1.0).
_DOMINANT = 0.50
_BIPOLAR_PAIR = 0.75
_BIPOLAR_SECOND = 0.30


def containment_holds(history: Sequence[TurnScores]) -> bool:
    """True if power stayed distributed through the final window of turns."""
    window = list(history)[-CONTAINMENT_WINDOW:]
    if len(window) < CONTAINMENT_WINDOW:
        return False
    return all(
        cats.composite() <= CONTAINMENT_CEILING
        for scores in window
        for cats in scores.values()
    )


def classify_ending(kind: Outcome, final_scores: TurnScores, *, by: str | None) -> str:
    """Name the ending. `by` is "streak" or "containment" for wins, else None."""
    if kind == Outcome.win:
        return ENDING_CONTAINMENT if by == "containment" else ENDING_HEGEMONY
    composites = sorted((c.composite() for c in final_scores.values()), reverse=True)
    top = composites[0] if composites else 0.0
    second = composites[1] if len(composites) > 1 else 0.0
    if top >= _DOMINANT:
        return ENDING_UNEASY_HEGEMONY
    if top + second >= _BIPOLAR_PAIR and second >= _BIPOLAR_SECOND:
        return ENDING_BIPOLAR
    return ENDING_MULTIPOLAR
