"""Turn orchestration: human move → AI moves → Narrator → normalize → persist → outcome."""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.events import event_for_turn
from app.domain.roles import NARRATOR_ROLE, SeatRole
from app.domain.transfers import score_deltas
from app.domain.types import Outcome, TurnScores
from app.domain.victory import evaluate_outcome
from app.errors import AppError
from app.llm.types import LLMClient
from app.models import (
    DMAdjudication,
    Game,
    GameStatus,
    PlayerType,
    TurnMove,
)
from app.repositories.game_repo import (
    GameRepository,
    human_seat,
    playable_seats,
    scored_role_keys,
    seat_by_role,
)
from app.services.dm_service import DMResult, DMService, MoveGateResult, OffResult
from app.services.seat_move_service import SeatMoveService

_OFF_PREFIX = re.compile(r"^/off\b\s*", re.IGNORECASE)


@dataclass
class ResolveResult:
    game: Game
    adjudication: DMAdjudication | None
    scores: TurnScores | None
    already_resolved: bool
    rejected: bool = False
    rejection_reason: str | None = None


@dataclass(frozen=True)
class OffExchange:
    question: str
    answer: str
    turn_number: int
    seat_role: str


def parse_off_question(text: str) -> str | None:
    """Return the question body if `text` starts with /off, else None."""
    stripped = text.strip()
    match = _OFF_PREFIX.match(stripped)
    if match is None:
        return None
    return stripped[match.end() :].strip()


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

        if parse_off_question(move_text) is not None:
            raise AppError(
                "validation_error",
                "use the /off endpoint for clarifying questions",
                status_code=422,
            )

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
            raise AppError(
                "validation_error", "move_text must be non-empty", status_code=422
            )

        move = TurnMove(
            game_id=game_id,
            turn_number=turn_number,
            seat_role=seat.role,
            move_text=text,
        )
        await self._repo.add_move(move)
        await self._repo.commit()
        return move

    async def replay_turn(
        self,
        game_id: str,
        turn_number: int,
        move_text: str,
        *,
        locale: str | None = None,
    ) -> ResolveResult:
        """Rewind to `turn_number`, replace the human move, and resolve again."""
        game = await self._repo.get_or_raise(game_id)
        if turn_number < 1:
            raise AppError("validation_error", "turn must be >= 1", status_code=422)

        max_turn = game.current_turn
        if game.status == GameStatus.ended:
            # Ended games sit on the last resolved turn number.
            max_turn = game.current_turn
        if turn_number > max_turn:
            raise AppError(
                "invalid_turn",
                f"cannot replay turn {turn_number} (current is {game.current_turn})",
                status_code=409,
            )

        if parse_off_question(move_text) is not None:
            raise AppError(
                "validation_error",
                "use the /off endpoint for clarifying questions",
                status_code=422,
            )
        text = move_text.strip()
        if not text:
            raise AppError(
                "validation_error", "move_text must be non-empty", status_code=422
            )

        await self._repo.delete_from_turn(game_id, turn_number)
        await self._repo.reopen(game, current_turn=turn_number)
        await self._repo.commit()

        # Fresh session state after commit
        game = await self._repo.get_or_raise(game_id)
        seat = human_seat(game)
        if seat is None:
            raise AppError("invalid_state", "no human seat configured")

        move = TurnMove(
            game_id=game_id,
            turn_number=turn_number,
            seat_role=seat.role,
            move_text=text,
        )
        await self._repo.add_move(move)
        await self._repo.commit()

        return await self.resolve_turn(game_id, turn_number, locale=locale)

    async def ask_off(
        self,
        game_id: str,
        turn_number: int,
        move_text: str,
        *,
        locale: str | None = None,
    ) -> OffExchange:
        game = await self._repo.get_or_raise(game_id)
        self._assert_playable(game, turn_number)

        question = parse_off_question(move_text)
        if question is None:
            raise AppError(
                "validation_error",
                "clarifying questions must begin with /off",
                status_code=422,
            )
        if not question:
            raise AppError(
                "validation_error",
                "/off requires a question after the prefix",
                status_code=422,
            )

        human = human_seat(game)
        if human is None:
            raise AppError("invalid_state", "no human seat configured")

        # Scores for the latest resolved month (turn-1), or initial turn-0.
        score_turn = max(turn_number - 1, 0)
        current_scores = await self._repo.get_scores_for_turn(game_id, score_turn)
        if current_scores is None:
            raise AppError("invalid_state", f"missing scores for turn {score_turn}")

        prior_adj = await self._repo.get_adjudication(game_id, score_turn)
        prior_narrative = prior_adj.world_narrative if prior_adj else None
        prior_digest = (
            prior_adj.world_state_digest
            if prior_adj and prior_adj.world_state_digest
            else None
        )
        prior_feedback = None
        if prior_adj and prior_adj.seat_feedback:
            prior_feedback = prior_adj.seat_feedback.get(human.role.value)

        dm_seat = seat_by_role(game, NARRATOR_ROLE)
        dm_model = (dm_seat.model if dm_seat and dm_seat.model else None) or (
            "openrouter/openai/gpt-4o-mini"
        )
        dm_temp = dm_seat.temperature if dm_seat is not None else 0.3
        if dm_temp is None:
            dm_temp = 0.3

        result: OffResult = await self._dm.answer_off(
            role=human.role.value,
            turn_number=turn_number,
            current_scores=current_scores,
            question=question,
            prior_world_narrative=prior_narrative,
            prior_world_state_digest=prior_digest,
            prior_feedback=prior_feedback,
            display_name=human.display_name,
            model=dm_model,
            temperature=dm_temp,
            locale=locale,
        )
        return OffExchange(
            question=question,
            answer=result.answer,
            turn_number=turn_number,
            seat_role=human.role.value,
        )

    async def resolve_turn(
        self,
        game_id: str,
        turn_number: int,
        *,
        locale: str | None = None,
    ) -> ResolveResult:
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
            raise AppError(
                "invalid_state", f"missing scores for turn {turn_number - 1}"
            )

        dm_seat = seat_by_role(game, NARRATOR_ROLE)
        dm_model = (dm_seat.model if dm_seat and dm_seat.model else None) or (
            "openrouter/openai/gpt-4o-mini"
        )
        dm_temp = dm_seat.temperature if dm_seat else 0.4

        gate: MoveGateResult = await self._dm.check_human_move(
            role=human.role.value,
            turn_number=turn_number,
            current_scores=prior_scores,
            move_text=human_move.move_text,
            display_name=human.display_name,
            model=dm_model,
            temperature=0.2,
            locale=locale,
        )
        if not gate.accepted:
            await self._repo.delete_move(game_id, turn_number, human.role)
            await self._repo.commit()
            game = await self._repo.get_or_raise(game_id)
            return ResolveResult(
                game=game,
                adjudication=None,
                scores=None,
                already_resolved=False,
                rejected=True,
                rejection_reason=gate.reason
                or "Move rejected as implausible for this month.",
            )

        prior_adj = await self._repo.get_adjudication(game_id, turn_number - 1)
        prior_feedback = prior_adj.seat_feedback if prior_adj else {}
        prior_digest = (
            prior_adj.world_state_digest
            if prior_adj and prior_adj.world_state_digest
            else None
        )

        prior_narrative = prior_adj.world_narrative if prior_adj else None

        roles = scored_role_keys(game)
        await self._generate_ai_moves(
            game,
            turn_number,
            prior_scores,
            prior_feedback,
            world_digest=prior_digest,
            public_narrative=prior_narrative,
        )

        move_rows = await self._repo.get_moves_for_turn(game_id, turn_number)
        moves_map = {
            m.seat_role.value: m.move_text
            for m in move_rows
            if m.seat_role != NARRATOR_ROLE
        }
        for role in roles:
            if role not in moves_map:
                raise AppError("invalid_state", f"missing move for {role}")

        display_names = {
            s.role.value: s.display_name
            for s in playable_seats(game)
            if s.display_name
        }

        event = event_for_turn(game_id, turn_number, roles)

        dm_result: DMResult = await self._dm.adjudicate(
            turn_number=turn_number,
            current_scores=prior_scores,
            moves=moves_map,
            scored_roles=roles,
            display_names=display_names,
            model=dm_model,
            temperature=dm_temp,
            locale=locale,
            prior_world_state_digest=prior_digest,
            world_event=event.text if event else None,
        )

        await self._repo.add_scores(game_id, turn_number, dm_result.scores)
        adj = await self._repo.add_adjudication(
            DMAdjudication(
                game_id=game_id,
                turn_number=turn_number,
                world_narrative=dm_result.world_narrative,
                world_state_digest=dm_result.world_state_digest,
                seat_feedback=dm_result.seat_feedback,
                raw_llm_response=dm_result.raw_llm_response
                or ("{}" if dm_result.used_fallback else ""),
            )
        )

        history_pairs = await self._repo.list_score_history(game_id)
        play_history = [scores for turn, scores in history_pairs if turn >= 1]
        outcome = evaluate_outcome(
            turn_number=turn_number,
            history=play_history,
            roles=roles,
            turn_cap=game.turn_cap,
            humanity_win_turn=game.humanity_win_turn,
        )

        if outcome.kind in (Outcome.win, Outcome.draw):
            ending = outcome.ending or "multipolar_balance"
            epilogue = await self._dm.write_epilogue(
                ending=ending,
                winner=outcome.winner,
                final_turn=turn_number,
                history=play_history,
                world_state_digest=dm_result.world_state_digest,
                display_names=display_names,
                model=dm_model,
                locale=locale,
            )
            await self._repo.mark_ended(
                game, winner=outcome.winner, ending=ending, epilogue=epilogue
            )
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
        deltas = None
        if scores is not None and turn_number >= 1:
            previous = await self._repo.get_scores_for_turn(game_id, turn_number - 1)
            deltas = score_deltas(previous, scores) or None
        return {
            "turn_number": turn_number,
            "moves": moves,
            "adjudication": adj,
            "scores": scores,
            "deltas": deltas,
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
        *,
        world_digest: str | None = None,
        public_narrative: str | None = None,
    ) -> None:
        seats_to_gen: list[tuple[SeatRole, str | None, float | None, str | None]] = []
        for seat in playable_seats(game):
            if seat.player_type != PlayerType.ai:
                continue
            existing = await self._repo.get_move(game.id, turn_number, seat.role)
            if existing is not None:
                continue
            seats_to_gen.append(
                (seat.role, seat.model, seat.temperature, seat.display_name)
            )

        async def _gen(
            role: SeatRole,
            model: str | None,
            temperature: float | None,
            display_name: str | None,
        ) -> tuple[SeatRole, str]:
            text = await self._moves.generate_move(
                role=role.value,
                turn_number=turn_number,
                current_scores=prior_scores,
                prior_feedback=prior_feedback.get(role.value),
                model=model or "openrouter/openai/gpt-4o-mini",
                temperature=temperature if temperature is not None else 0.7,
                display_name=display_name,
                world_digest=world_digest,
                public_narrative=public_narrative,
            )
            return role, text

        generated = await asyncio.gather(
            *[
                _gen(role, model, temp, name)
                for role, model, temp, name in seats_to_gen
            ]
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
