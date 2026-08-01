"""Create and read games."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.scoring import initial_scores
from app.errors import AppError
from app.models import Game, GameStatus, PlayerType, Seat, SeatRole
from app.repositories.game_repo import GameRepository


REQUIRED_ROLES = (
    SeatRole.rogue_ai,
    SeatRole.defender_ai,
    SeatRole.dm,
    SeatRole.humanity,
)


@dataclass
class SeatConfig:
    role: SeatRole
    player_type: PlayerType
    model: str | None = None
    temperature: float | None = None


class GameService:
    def __init__(self, session: AsyncSession):
        self._repo = GameRepository(session)

    async def create_game(self, seats: list[SeatConfig] | None = None) -> Game:
        if seats is None:
            seats = default_mvp_seats()
        _validate_seats(seats)

        game = Game(
            status=GameStatus.in_progress,
            current_turn=1,
            turn_cap=60,
            humanity_win_turn=30,
        )
        await self._repo.add(game)
        for cfg in seats:
            await self._repo.add_seat(
                Seat(
                    game_id=game.id,
                    role=cfg.role,
                    player_type=cfg.player_type,
                    model=cfg.model,
                    temperature=cfg.temperature,
                )
            )
        await self._repo.add_scores(game.id, 0, initial_scores())
        await self._repo.commit()
        return await self._repo.get_or_raise(game.id)

    async def get_game(self, game_id: str) -> Game:
        return await self._repo.get_or_raise(game_id)


def default_mvp_seats() -> list[SeatConfig]:
    """MVP: humanity human; rogue/defender/dm AI (Open Gate 2.13 provisional)."""
    default_model = "openrouter/openai/gpt-4o-mini"
    return [
        SeatConfig(SeatRole.rogue_ai, PlayerType.ai, default_model, 0.7),
        SeatConfig(SeatRole.defender_ai, PlayerType.ai, default_model, 0.7),
        SeatConfig(SeatRole.dm, PlayerType.ai, default_model, 0.4),
        SeatConfig(SeatRole.humanity, PlayerType.human, None, None),
    ]


def _validate_seats(seats: list[SeatConfig]) -> None:
    roles = {s.role for s in seats}
    missing = set(REQUIRED_ROLES) - roles
    if missing:
        raise AppError(
            "validation_error",
            f"missing seats: {sorted(r.value for r in missing)}",
            status_code=422,
        )
    if len(seats) != len(REQUIRED_ROLES):
        raise AppError("validation_error", "exactly 4 seats required", status_code=422)
    humans = [s for s in seats if s.player_type == PlayerType.human]
    if len(humans) != 1:
        raise AppError(
            "validation_error",
            "exactly one human seat required in MVP",
            status_code=422,
        )
    if humans[0].role == SeatRole.dm:
        raise AppError(
            "validation_error",
            "DM cannot be the human seat",
            status_code=422,
        )
