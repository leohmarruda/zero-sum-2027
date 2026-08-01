"""Generate free-text moves for AI-controlled scored seats."""

from __future__ import annotations

from app.domain.types import TurnScores
from app.llm.prompts import ROLE_BLURBS, build_seat_move_prompt, narrative_date_for_turn
from app.llm.types import LLMClient, LLMClientError

DEFAULT_SEAT_MODEL = "openrouter/openai/gpt-4o-mini"


class SeatMoveService:
    def __init__(self, llm: LLMClient):
        self._llm = llm

    async def generate_move(
        self,
        *,
        role: str,
        turn_number: int,
        current_scores: TurnScores,
        prior_feedback: str | None,
        model: str = DEFAULT_SEAT_MODEL,
        temperature: float | None = 0.7,
    ) -> str:
        if role not in ROLE_BLURBS:
            raise ValueError(f"unsupported seat role for move gen: {role}")
        system, user = build_seat_move_prompt(
            role=role,
            turn_number=turn_number,
            narrative_date=narrative_date_for_turn(turn_number),
            current_scores=current_scores,
            prior_feedback=prior_feedback,
        )
        try:
            out = await self._llm.complete(
                model,
                user,
                system=system,
                temperature=temperature,
                response_format="text",
                max_tokens=800,
            )
            text = out.content.strip()
            return text or f"({role} remains quiet this month.)"
        except LLMClientError:
            return f"({role} failed to transmit a coherent plan this month.)"
