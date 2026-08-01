"""Turn orchestration: human move → AI moves → DM → normalize → persist → outcome."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.types import Outcome, TurnScores
from app.domain.victory import evaluate_outcome
from app.errors import AppError
from app.llm.types import LLMClient
from app.models import (
    DMAdjudication,
    Game,
    GameStatus,
    PlayerType,
    SeatRole,
    TurnMove,
)
from app.repositories.game_repo import GameRepository, human_seat, seat_by_role
from app.services.dm_service import DMResult, DMService
from app.services.seat_move_service import SeatMoveService

SCORED_AI_ROLES = (SeatRole.rogue_ai, SeatRole.defender_ai, SeatRole.humanity)


@dataclass
class ResolveResult:
    game: Game
    adjudication: DMAdjudication
    scores: TurnScores
    already_resolved: bool


class TurnService:
    def __init__(self, session: AsyncSession, llm: LLMClient):
        self._repo = GameRepository(session)
        self._dm = DMService(llm)
        self._moves = SeatMoveService(llm)

    async def submit_human_move(
        self, game_id: str, turn_number: int, move_text: str
    ) -> TurnMove:
        game = await self._repo.get_or_raise(game_id)
        self._assert_playable(game, turn_number)

        seat = human_seat(game)
        if seat is None:
            raise AppError("invalid_state", "no human seat configured")

        existing = await self._repo.get_move(game_id, turn_number, seat.role)
        if existing is not None:
            raise AppError(
                "conflict",
                "human move already submitted for this turn",
                status_code=409,
            )

        text = move_text.strip()
        if not text:
            raise AppError("validation_error", "move_text must be non-empty", status_code=422)

        move = TurnMove(
            game_id=game_id,
            turn_number=turn_number,
            seat_role=seat.role,
            move_text=text,
        )
        await self._repo.add_move(move)
        await self._repo.commit()
        return move

    async def resolve_turn(self, game_id: str, turn_number: int) -> ResolveResult:
        game = await self._repo.get_or_raise(game_id)

        existing_adj = await self._repo.get_adjudication(game_id, turn_number)
        if existing_adj is not None:
            scores = await self._repo.get_scores_for_turn(game_id, turn_number)
            if scores is None:
                raise AppError("invalid_state", "adjudication without scores")
            return ResolveResult(
                game=game,
                adjudication=existing_adj,
                scores=scores,
                already_resolved=True,
            )

        self._assert_playable(game, turn_number)

        human = human_seat(game)
        if human is None:
            raise AppError("invalid_state", "no human seat configured")
        human_move = await self._repo.get_move(game_id, turn_number, human.role)
        if human_move is None:
            raise AppError(
                "precondition_failed",
                "human move required before resolve",
                status_code=409,
            )

        prior_scores = await self._repo.get_scores_for_turn(game_id, turn_number - 1)
        if prior_scores is None:
            raise AppError("invalid_state", f"missing scores for turn {turn_number - 1}")

        prior_adj = await self._repo.get_adjudication(game_id, turn_number - 1)
        prior_feedback = prior_adj.seat_feedback if prior_adj else {}

        # Generate AI scored-seat moves in parallel (blind — no peer texts).
        await self._generate_ai_moves(game, turn_number, prior_scores, prior_feedback)

        move_rows = await self._repo.get_moves_for_turn(game_id, turn_number)
        moves_map = {
            m.seat_role.value: m.move_text
            for m in move_rows
            if m.seat_role in SCORED_AI_ROLES
        }
        for role in SCORED_AI_ROLES:
            if role.value not in moves_map:
                raise AppError("invalid_state", f"missing move for {role.value}")

        dm_seat = seat_by_role(game, SeatRole.dm)
        dm_model = (dm_seat.model if dm_seat and dm_seat.model else None) or "openrouter/openai/gpt-4o-mini"
        dm_temp = dm_seat.temperature if dm_seat else 0.4

        dm_result: DMResult = await self._dm.adjudicate(
            turn_number=turn_number,
            current_scores=prior_scores,
            moves=moves_map,
            model=dm_model,
            temperature=dm_temp,
        )

        await self._repo.add_scores(game_id, turn_number, dm_result.scores)
        adj = await self._repo.add_adjudication(
            DMAdjudication(
                game_id=game_id,
                turn_number=turn_number,
                world_narrative=dm_result.world_narrative,
                seat_feedback=dm_result.seat_feedback,
                raw_llm_response=dm_result.raw_llm_response
                or ("{}" if dm_result.used_fallback else ""),
            )
        )

        history_pairs = await self._repo.list_score_history(game_id)
        # Streaks count resolved play turns only (exclude turn 0 baseline).
        play_history = [scores for turn, scores in history_pairs if turn >= 1]
        outcome = evaluate_outcome(
            turn_number=turn_number,
            history=play_history,
            turn_cap=game.turn_cap,
            humanity_win_turn=game.humanity_win_turn,
        )

        if outcome.kind == Outcome.win:
            await self._repo.mark_ended(game, winner=outcome.winner)
        elif outcome.kind == Outcome.draw:
            await self._repo.mark_ended(game, winner=None)
        else:
            game.current_turn = turn_number + 1

        await self._repo.commit()
        game = await self._repo.get_or_raise(game_id)
        return ResolveResult(
            game=game,
            adjudication=adj,
            scores=dm_result.scores,
            already_resolved=False,
        )

    async def get_turn(self, game_id: str, turn_number: int) -> dict:
        await self._repo.get_or_raise(game_id)
        moves = await self._repo.get_moves_for_turn(game_id, turn_number)
        adj = await self._repo.get_adjudication(game_id, turn_number)
        scores = await self._repo.get_scores_for_turn(game_id, turn_number)
        return {
            "turn_number": turn_number,
            "moves": moves,
            "adjudication": adj,
            "scores": scores,
        }

    async def get_history(self, game_id: str) -> list[tuple[int, TurnScores]]:
        await self._repo.get_or_raise(game_id)
        return await self._repo.list_score_history(game_id)

    async def _generate_ai_moves(
        self,
        game: Game,
        turn_number: int,
        prior_scores: TurnScores,
        prior_feedback: dict,
    ) -> None:
        seats_to_gen: list[tuple[SeatRole, str | None, float | None]] = []
        for role in SCORED_AI_ROLES:
            seat = seat_by_role(game, role)
            if seat is None or seat.player_type != PlayerType.ai:
                continue
            existing = await self._repo.get_move(game.id, turn_number, role)
            if existing is not None:
                continue
            seats_to_gen.append((role, seat.model, seat.temperature))

        async def _gen(
            role: SeatRole, model: str | None, temperature: float | None
        ) -> tuple[SeatRole, str]:
            text = await self._moves.generate_move(
                role=role.value,
                turn_number=turn_number,
                current_scores=prior_scores,
                prior_feedback=prior_feedback.get(role.value),
                model=model or "openrouter/openai/gpt-4o-mini",
                temperature=temperature if temperature is not None else 0.7,
            )
            return role, text

        # Parallelize LLM calls only; persist sequentially (session is not concurrent-safe).
        generated = await asyncio.gather(
            *[_gen(role, model, temp) for role, model, temp in seats_to_gen]
        )
        for role, text in generated:
            await self._repo.add_move(
                TurnMove(
                    game_id=game.id,
                    turn_number=turn_number,
                    seat_role=role,
                    move_text=text,
                )
            )

    def _assert_playable(self, game: Game, turn_number: int) -> None:
        if game.status == GameStatus.ended:
            raise AppError("game_ended", "game already ended", status_code=409)
        if turn_number != game.current_turn:
            raise AppError(
                "invalid_turn",
                f"expected turn {game.current_turn}, got {turn_number}",
                status_code=409,
            )
