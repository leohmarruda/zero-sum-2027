"""Pydantic request/response schemas for the game API."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

SeatRoleLiteral = Literal["rogue_ai", "defender_ai", "dm", "humanity"]
PlayerTypeLiteral = Literal["human", "ai"]
GameStatusLiteral = Literal["setup", "in_progress", "ended"]
ScoredRoleLiteral = Literal["rogue_ai", "defender_ai", "humanity"]


class SeatIn(BaseModel):
    role: SeatRoleLiteral
    player_type: PlayerTypeLiteral
    model: str | None = None
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)


class CreateGameRequest(BaseModel):
    seats: list[SeatIn] | None = None


class SeatOut(BaseModel):
    role: SeatRoleLiteral
    player_type: PlayerTypeLiteral
    model: str | None
    temperature: float | None


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
    ended_at: datetime | None
    seats: list[SeatOut]
    current_scores: dict[ScoredRoleLiteral, CategoryScoresOut] | None = None


class SubmitMoveRequest(BaseModel):
    move_text: str = Field(min_length=1)


class MoveOut(BaseModel):
    seat_role: SeatRoleLiteral
    move_text: str
    turn_number: int


class AdjudicationOut(BaseModel):
    turn_number: int
    world_narrative: str
    seat_feedback: dict[str, str]


class TurnOut(BaseModel):
    turn_number: int
    moves: list[MoveOut]
    adjudication: AdjudicationOut | None
    scores: dict[ScoredRoleLiteral, CategoryScoresOut] | None


class ResolveOut(BaseModel):
    game: GameOut
    turn: TurnOut
    already_resolved: bool


class HistoryPointOut(BaseModel):
    turn_number: int
    scores: dict[ScoredRoleLiteral, CategoryScoresOut]


class HistoryOut(BaseModel):
    game_id: str
    history: list[HistoryPointOut]
