"""Domain types for scores and game outcomes."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal

ScoredRole = Literal["rogue_ai", "defender_ai", "humanity"]
ScoreCategory = Literal["sm", "rc", "ic", "pc", "cs"]

SCORED_ROLES: tuple[ScoredRole, ...] = ("rogue_ai", "defender_ai", "humanity")
SCORE_CATEGORIES: tuple[ScoreCategory, ...] = ("sm", "rc", "ic", "pc", "cs")

# Composite score = equal weight across 5 categories; win threshold is 0.9
# of the 0–1 composite (i.e. average category share ≥ 90).
WIN_THRESHOLD = 0.9
WIN_STREAK_REQUIRED = 10
DEFAULT_TURN_CAP = 60
HUMANITY_WIN_TURN = 30


class Outcome(str, Enum):
    continue_ = "continue"
    win = "win"
    draw = "draw"


@dataclass(frozen=True)
class CategoryScores:
    """One seat's shares for the five categories (0–100 each)."""

    sm: float
    rc: float
    ic: float
    pc: float
    cs: float

    def as_dict(self) -> dict[ScoreCategory, float]:
        return {
            "sm": self.sm,
            "rc": self.rc,
            "ic": self.ic,
            "pc": self.pc,
            "cs": self.cs,
        }

    def composite(self) -> float:
        """Mean share as a 0–1 fraction (category values are 0–100)."""
        total = self.sm + self.rc + self.ic + self.pc + self.cs
        return (total / 5.0) / 100.0


TurnScores = dict[ScoredRole, CategoryScores]


@dataclass(frozen=True)
class GameOutcome:
    kind: Outcome
    winner: ScoredRole | None = None
