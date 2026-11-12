"""Create and read games."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.roles import (
    DEFAULT_PLAYABLE_ROLES,
    NARRATOR_ROLE,
    PLAYABLE_ROLES,
    SeatRole,
)
from app.domain.scoring import initial_scores
from app.errors import AppError
from app.models import Game, GameStatus, PlayerType, Seat
from app.repositories.game_repo import GameRepository

DEFAULT_MODEL = "openrouter/openai/gpt-4o-mini"
MIN_PLAYABLE_SEATS = 2
MAX_PLAYABLE_SEATS = len(PLAYABLE_ROLES)


@dataclass
class SeatConfig:
    role: SeatRole
    player_type: PlayerType
    model: str | None = None
    temperature: float | None = None
    display_name: str | None = None


class GameService:
    def __init__(self, session: AsyncSession):
        self._repo = GameRepository(session)

    async def create_game(self, seats: list[SeatConfig] | None = None) -> Game:
        if seats is None:
            seats = default_mvp_seats()
        _validate_seats(seats)

        playable = [s for s in seats if s.role != NARRATOR_ROLE]
        scored_roles = [s.role.value for s in playable]

        game = Game(
            status=GameStatus.in_progress,
            current_turn=1,
            turn_cap=60,
            humanity_win_turn=30,
        )
        await self._repo.add(game)
        for cfg in seats:
            name = (cfg.display_name or "").strip() or None
            await self._repo.add_seat(
                Seat(
                    game_id=game.id,
                    role=cfg.role,
                    player_type=cfg.player_type,
                    display_name=name,
                    model=cfg.model,
                    temperature=cfg.temperature,
                )
            )
        await self._repo.add_scores(game.id, 0, initial_scores(scored_roles))
        await self._repo.commit()
        return await self._repo.get_or_raise(game.id)

    async def get_game(self, game_id: str) -> Game:
        return await self._repo.get_or_raise(game_id)


def default_mvp_seats() -> list[SeatConfig]:
    """Default: HWG (human) + Defender AI + Selfish AI + Narrator."""
    seats: list[SeatConfig] = []
    for role in DEFAULT_PLAYABLE_ROLES:
        if role == SeatRole.hwg:
            seats.append(SeatConfig(role, PlayerType.human, None, None))
        else:
            seats.append(SeatConfig(role, PlayerType.ai, DEFAULT_MODEL, 0.7))
    seats.append(SeatConfig(NARRATOR_ROLE, PlayerType.ai, DEFAULT_MODEL, 0.4))
    return seats


def _validate_seats(seats: list[SeatConfig]) -> None:
    if not seats:
        raise AppError("validation_error", "seats required", status_code=422)

    roles = [s.role for s in seats]
    if len(roles) != len(set(roles)):
        raise AppError("validation_error", "duplicate roles are not allowed", status_code=422)

    if NARRATOR_ROLE not in roles:
        raise AppError("validation_error", "Narrator seat is required", status_code=422)

    narrators = [s for s in seats if s.role == NARRATOR_ROLE]
    if len(narrators) != 1:
        raise AppError("validation_error", "exactly one Narrator seat required", status_code=422)
    if narrators[0].player_type != PlayerType.ai:
        raise AppError(
            "validation_error",
            "Narrator must be an AI seat",
            status_code=422,
        )

    playable = [s for s in seats if s.role != NARRATOR_ROLE]
    if len(playable) < MIN_PLAYABLE_SEATS:
        raise AppError(
            "validation_error",
            f"at least {MIN_PLAYABLE_SEATS} playable seats required",
            status_code=422,
        )
    if len(playable) > MAX_PLAYABLE_SEATS:
        raise AppError(
            "validation_error",
            f"at most {MAX_PLAYABLE_SEATS} playable seats allowed",
            status_code=422,
        )
    for seat in playable:
        if seat.role not in PLAYABLE_ROLES:
            raise AppError(
                "validation_error",
                f"unsupported playable role: {seat.role.value}",
                status_code=422,
            )

    humans = [s for s in playable if s.player_type == PlayerType.human]
    if len(humans) != 1:
        raise AppError(
            "validation_error",
            "exactly one human playable seat required",
            status_code=422,
        )

    for seat in seats:
        if seat.display_name and len(seat.display_name.strip()) > 64:
            raise AppError(
                "validation_error",
                "display_name must be at most 64 characters",
                status_code=422,
            )
