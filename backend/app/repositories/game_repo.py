"""Persistence for games, seats, moves, scores, and DM adjudications."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.roles import NARRATOR_ROLE, SeatRole, is_playable
from app.domain.types import CategoryScores, ScoredRole, TurnScores
from app.models import (
    DMAdjudication,
    Game,
    GameStatus,
    PlayerType,
    ScoreSnapshot,
    Seat,
    TurnMove,
)


class GameRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, game: Game) -> Game:
        self._session.add(game)
        await self._session.flush()
        return game

    async def get(self, game_id: str) -> Game | None:
        stmt = (
            select(Game)
            .where(Game.id == game_id)
            .options(
                selectinload(Game.seats),
                selectinload(Game.scores),
                selectinload(Game.moves),
                selectinload(Game.adjudications),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_raise(self, game_id: str) -> Game:
        game = await self.get(game_id)
        if game is None:
            from app.errors import AppError

            raise AppError("not_found", f"game {game_id} not found", status_code=404)
        return game

    async def add_seat(self, seat: Seat) -> Seat:
        self._session.add(seat)
        await self._session.flush()
        return seat

    async def add_scores(
        self, game_id: str, turn_number: int, scores: TurnScores
    ) -> list[ScoreSnapshot]:
        rows: list[ScoreSnapshot] = []
        for role, cats in scores.items():
            row = ScoreSnapshot(
                game_id=game_id,
                turn_number=turn_number,
                seat_role=SeatRole(role),
                sm=cats.sm,
                rc=cats.rc,
                ic=cats.ic,
                pc=cats.pc,
                cs=cats.cs,
            )
            self._session.add(row)
            rows.append(row)
        await self._session.flush()
        return rows

    async def get_scores_for_turn(
        self, game_id: str, turn_number: int
    ) -> TurnScores | None:
        stmt = select(ScoreSnapshot).where(
            ScoreSnapshot.game_id == game_id,
            ScoreSnapshot.turn_number == turn_number,
        )
        result = await self._session.execute(stmt)
        rows = list(result.scalars().all())
        if not rows:
            return None
        out: TurnScores = {}
        for row in rows:
            if not is_playable(row.seat_role):
                continue
            role: ScoredRole = row.seat_role.value
            out[role] = CategoryScores(
                sm=row.sm, rc=row.rc, ic=row.ic, pc=row.pc, cs=row.cs
            )
        return out or None

    async def list_score_history(self, game_id: str) -> list[tuple[int, TurnScores]]:
        """Return (turn_number, scores) ordered ascending, including turn 0."""
        stmt = (
            select(ScoreSnapshot)
            .where(ScoreSnapshot.game_id == game_id)
            .order_by(ScoreSnapshot.turn_number)
        )
        result = await self._session.execute(stmt)
        by_turn: dict[int, TurnScores] = {}
        for row in result.scalars().all():
            if not is_playable(row.seat_role):
                continue
            role: ScoredRole = row.seat_role.value
            by_turn.setdefault(row.turn_number, {})[role] = CategoryScores(
                sm=row.sm, rc=row.rc, ic=row.ic, pc=row.pc, cs=row.cs
            )
        # Keep turns that have at least one scored seat (size may vary only if corrupt).
        return [(t, scores) for t, scores in sorted(by_turn.items()) if scores]

    async def add_move(self, move: TurnMove) -> TurnMove:
        self._session.add(move)
        await self._session.flush()
        return move

    async def get_moves_for_turn(
        self, game_id: str, turn_number: int
    ) -> list[TurnMove]:
        stmt = select(TurnMove).where(
            TurnMove.game_id == game_id,
            TurnMove.turn_number == turn_number,
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_move(
        self, game_id: str, turn_number: int, role: SeatRole
    ) -> TurnMove | None:
        stmt = select(TurnMove).where(
            TurnMove.game_id == game_id,
            TurnMove.turn_number == turn_number,
            TurnMove.seat_role == role,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_move(
        self, game_id: str, turn_number: int, role: SeatRole
    ) -> None:
        await self._session.execute(
            delete(TurnMove).where(
                TurnMove.game_id == game_id,
                TurnMove.turn_number == turn_number,
                TurnMove.seat_role == role,
            )
        )
        await self._session.flush()

    async def get_adjudication(
        self, game_id: str, turn_number: int
    ) -> DMAdjudication | None:
        stmt = select(DMAdjudication).where(
            DMAdjudication.game_id == game_id,
            DMAdjudication.turn_number == turn_number,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def add_adjudication(self, adj: DMAdjudication) -> DMAdjudication:
        self._session.add(adj)
        await self._session.flush()
        return adj

    async def delete_from_turn(self, game_id: str, from_turn: int) -> None:
        """Remove moves, adjudications, and scores for turn >= from_turn (keep turn 0)."""
        await self._session.execute(
            delete(TurnMove).where(
                TurnMove.game_id == game_id,
                TurnMove.turn_number >= from_turn,
            )
        )
        await self._session.execute(
            delete(DMAdjudication).where(
                DMAdjudication.game_id == game_id,
                DMAdjudication.turn_number >= from_turn,
            )
        )
        await self._session.execute(
            delete(ScoreSnapshot).where(
                ScoreSnapshot.game_id == game_id,
                ScoreSnapshot.turn_number >= from_turn,
            )
        )
        await self._session.flush()

    async def reopen(self, game: Game, *, current_turn: int) -> Game:
        game.status = GameStatus.in_progress
        game.winner = None
        game.ending = None
        game.epilogue = None
        game.ended_at = None
        game.current_turn = current_turn
        await self._session.flush()
        return game

    async def mark_ended(
        self,
        game: Game,
        *,
        winner: str | None,
        ending: str | None = None,
        epilogue: str | None = None,
    ) -> Game:
        game.status = GameStatus.ended
        game.winner = winner
        game.ending = ending
        game.epilogue = epilogue
        game.ended_at = datetime.now(UTC)
        await self._session.flush()
        return game

    async def commit(self) -> None:
        await self._session.commit()


def seat_by_role(game: Game, role: SeatRole) -> Seat | None:
    for seat in game.seats:
        if seat.role == role:
            return seat
    return None


def human_seat(game: Game) -> Seat | None:
    for seat in game.seats:
        if seat.player_type == PlayerType.human and seat.role != NARRATOR_ROLE:
            return seat
    return None


def playable_seats(game: Game) -> list[Seat]:
    return [s for s in game.seats if s.role != NARRATOR_ROLE]


def scored_role_keys(game: Game) -> list[str]:
    return [s.role.value for s in playable_seats(game)]
