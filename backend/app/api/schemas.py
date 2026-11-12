"""Pydantic request/response schemas for the game API."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

SeatRoleLiteral = Literal[
    "paperclip_max",
    "selfish_ai",
    "paternalistic_ai",
    "defender_ai",
    "exterminator_ai",
    "hwg",
    "us",
    "china",
    "eu",
    "het",
    "gray_aliens",
    "narrator",
]
PlayerTypeLiteral = Literal["human", "ai"]
GameStatusLiteral = Literal["setup", "in_progress", "ended"]


class SeatIn(BaseModel):
    role: SeatRoleLiteral
    player_type: PlayerTypeLiteral
    model: str | None = None
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    display_name: str | None = Field(default=None, max_length=64)


class CreateGameRequest(BaseModel):
    seats: list[SeatIn] | None = None
    locale: str | None = None


class ContentOut(BaseModel):
    locale: str
    setup_intro: str
    narrator_intro_lines: dict[str, str]


class SeatOut(BaseModel):
    role: SeatRoleLiteral
    player_type: PlayerTypeLiteral
    model: str | None
    temperature: float | None
    display_name: str | None = None


class CategoryScoresOut(BaseModel):
    sm: float
    rc: float
    ic: float
    pc: float
    cs: float


class GameOut(BaseModel):
    id: str
    status: GameStatusLiteral
    current_turn: int
    turn_cap: int
    humanity_win_turn: int
    winner: str | None
    ending: str | None = None
    epilogue: str | None = None
    ended_at: datetime | None
    seats: list[SeatOut]
    current_scores: dict[str, CategoryScoresOut] | None = None
    narrator_intro: str | None = None


class SubmitMoveRequest(BaseModel):
    move_text: str = Field(min_length=1)
    locale: str | None = None


class OffAskRequest(BaseModel):
    move_text: str = Field(min_length=1)
    locale: str | None = None


class OffAskOut(BaseModel):
    turn_number: int
    seat_role: SeatRoleLiteral
    question: str
    answer: str


class MoveOut(BaseModel):
    seat_role: SeatRoleLiteral
    move_text: str
    turn_number: int


class AdjudicationOut(BaseModel):
    turn_number: int
    world_narrative: str
    world_state_digest: str = ""
    seat_feedback: dict[str, str]


class TurnOut(BaseModel):
    turn_number: int
    moves: list[MoveOut]
    adjudication: AdjudicationOut | None
    scores: dict[str, CategoryScoresOut] | None
    # seat role -> category -> signed change versus the previous turn's snapshot
    deltas: dict[str, dict[str, float]] | None = None


class ResolveOut(BaseModel):
    game: GameOut
    turn: TurnOut
    already_resolved: bool
    rejected: bool = False
    rejection_reason: str | None = None


class HistoryPointOut(BaseModel):
    turn_number: int
    scores: dict[str, CategoryScoresOut]


class HistoryOut(BaseModel):
    game_id: str
    history: list[HistoryPointOut]
