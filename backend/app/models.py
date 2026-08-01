"""ORM models — Game, Seat, TurnMove, ScoreSnapshot, DMAdjudication."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db import Base


class GameStatus(str, enum.Enum):
    setup = "setup"
    in_progress = "in_progress"
    ended = "ended"


class SeatRole(str, enum.Enum):
    rogue_ai = "rogue_ai"
    defender_ai = "defender_ai"
    dm = "dm"
    humanity = "humanity"


class PlayerType(str, enum.Enum):
    human = "human"
    ai = "ai"


SCORED_ROLES = (SeatRole.rogue_ai, SeatRole.defender_ai, SeatRole.humanity)
SCORE_CATEGORIES = ("sm", "rc", "ic", "pc", "cs")


def _uuid() -> str:
    return str(uuid.uuid4())


class Game(Base):
    __tablename__ = "games"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    status: Mapped[GameStatus] = mapped_column(
        Enum(GameStatus), default=GameStatus.setup, nullable=False
    )
    current_turn: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    turn_cap: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    humanity_win_turn: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    winner: Mapped[str | None] = mapped_column(String(32), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    seats: Mapped[list[Seat]] = relationship(back_populates="game", cascade="all, delete-orphan")
    moves: Mapped[list[TurnMove]] = relationship(
        back_populates="game", cascade="all, delete-orphan"
    )
    scores: Mapped[list[ScoreSnapshot]] = relationship(
        back_populates="game", cascade="all, delete-orphan"
    )
    adjudications: Mapped[list[DMAdjudication]] = relationship(
        back_populates="game", cascade="all, delete-orphan"
    )


class Seat(Base):
    __tablename__ = "seats"
    __table_args__ = (UniqueConstraint("game_id", "role", name="uq_seat_game_role"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    game_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("games.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[SeatRole] = mapped_column(Enum(SeatRole), nullable=False)
    player_type: Mapped[PlayerType] = mapped_column(Enum(PlayerType), nullable=False)
    model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)

    game: Mapped[Game] = relationship(back_populates="seats")


class TurnMove(Base):
    __tablename__ = "turn_moves"
    __table_args__ = (
        UniqueConstraint("game_id", "turn_number", "seat_role", name="uq_move_turn_seat"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    game_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("games.id", ondelete="CASCADE"), nullable=False
    )
    turn_number: Mapped[int] = mapped_column(Integer, nullable=False)
    seat_role: Mapped[SeatRole] = mapped_column(Enum(SeatRole), nullable=False)
    move_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    game: Mapped[Game] = relationship(back_populates="moves")


class ScoreSnapshot(Base):
    __tablename__ = "score_snapshots"
    __table_args__ = (
        UniqueConstraint(
            "game_id", "turn_number", "seat_role", name="uq_score_turn_seat"
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    game_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("games.id", ondelete="CASCADE"), nullable=False
    )
    turn_number: Mapped[int] = mapped_column(Integer, nullable=False)
    seat_role: Mapped[SeatRole] = mapped_column(Enum(SeatRole), nullable=False)
    sm: Mapped[float] = mapped_column(Float, nullable=False)
    rc: Mapped[float] = mapped_column(Float, nullable=False)
    ic: Mapped[float] = mapped_column(Float, nullable=False)
    pc: Mapped[float] = mapped_column(Float, nullable=False)
    cs: Mapped[float] = mapped_column(Float, nullable=False)

    game: Mapped[Game] = relationship(back_populates="scores")


class DMAdjudication(Base):
    __tablename__ = "dm_adjudications"
    __table_args__ = (
        UniqueConstraint("game_id", "turn_number", name="uq_adj_game_turn"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    game_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("games.id", ondelete="CASCADE"), nullable=False
    )
    turn_number: Mapped[int] = mapped_column(Integer, nullable=False)
    world_narrative: Mapped[str] = mapped_column(Text, nullable=False)
    seat_feedback: Mapped[dict] = mapped_column(JSON, nullable=False)
    raw_llm_response: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    game: Mapped[Game] = relationship(back_populates="adjudications")
