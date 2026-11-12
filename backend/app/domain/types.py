"""Domain types for scores and game outcomes."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal

# Role keys are catalog strings (see app.domain.roles); kept open for N seats.
ScoredRole = str
ScoreCategory = Literal["pc", "rc", "cs", "ic", "sm"]

# Display / adjudication order. DB column names stay pc/rc/cs/ic/sm.
SCORE_CATEGORIES: tuple[ScoreCategory, ...] = ("pc", "rc", "cs", "ic", "sm")

# Short English labels + definitions for Narrator adjudication and docs.
SCORE_CATEGORY_DEFS: dict[ScoreCategory, tuple[str, str]] = {
    "pc": (
        "Computing power",
        "Frontier FLOPs and their allocation: chips, clusters, inference "
        "contracts, model weights",
    ),
    "rc": (
        "Resources",
        "Non-substitutable primary inputs within ≤12 months: primary energy, "
        "critical minerals, lithography capacity, industrial water",
    ),
    "cs": (
        "Supply chain",
        "Capacity to transform inputs into goods: fabs, assembly lines, "
        "industrial robotics, freight logistics",
    ),
    "ic": (
        "Infrastructure",
        "Social continuity networks: grid, telecom, financial system, "
        "water/sanitation, health",
    ),
    "sm": (
        "Coercive power",
        "Capacity to impose outcomes by force or threat: armed forces, "
        "cyber offense, law enforcement, territorial control",
    ),
}

# Composite score = equal weight across 5 categories (0–1 mean share).
# Win threshold depends on N scored seats (excl. narrator): 0.85 + 0.15/N.
# Default 3-seat lineup → 0.9.
WIN_THRESHOLD_BASE = 0.85
WIN_THRESHOLD_SHARE = 0.15
WIN_STREAK_REQUIRED = 10
DEFAULT_TURN_CAP = 60
HUMANITY_WIN_TURN = 30


def win_threshold(n_roles: int) -> float:
    """Composite needed to count toward a win streak for N scored seats."""
    if n_roles < 1:
        raise ValueError("n_roles must be >= 1")
    return WIN_THRESHOLD_BASE + WIN_THRESHOLD_SHARE / n_roles


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
        return {cat: getattr(self, cat) for cat in SCORE_CATEGORIES}

    def composite(self) -> float:
        """Mean share as a 0–1 fraction (category values are 0–100)."""
        total = self.sm + self.rc + self.ic + self.pc + self.cs
        return (total / 5.0) / 100.0


TurnScores = dict[ScoredRole, CategoryScores]


@dataclass(frozen=True)
class GameOutcome:
    kind: Outcome
    winner: ScoredRole | None = None
    # How the game ended (see app.domain.endings); None while it continues.
    ending: str | None = None
