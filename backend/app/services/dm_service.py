"""DM adjudication service — parse structured JSON, fallback on failure."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass

from app.domain.scoring import normalize_turn_scores
from app.domain.types import (
    SCORE_CATEGORIES,
    SCORED_ROLES,
    CategoryScores,
    ScoredRole,
    TurnScores,
)
from app.llm.prompts import build_dm_prompt, narrative_date_for_turn
from app.llm.types import LLMClient, LLMClientError

logger = logging.getLogger(__name__)

DEFAULT_DM_MODEL = "openrouter/openai/gpt-4o-mini"


@dataclass(frozen=True)
class DMResult:
    world_narrative: str
    seat_feedback: dict[str, str]
    scores: TurnScores
    raw_llm_response: str
    used_fallback: bool = False


def _parse_scores(raw_scores: dict) -> TurnScores:
    out: TurnScores = {}
    for role in SCORED_ROLES:
        block = raw_scores[role]
        out[role] = CategoryScores(
            **{cat: float(block[cat]) for cat in SCORE_CATEGORIES}
        )
    return out


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        # drop first fence and optional last fence
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)
    return json.loads(text)


def fallback_result(prior: TurnScores, reason: str) -> DMResult:
    feedback = {role: "Communication failure with the DM this month." for role in SCORED_ROLES}
    return DMResult(
        world_narrative=(
            f"Global channels glitched ({reason}). Power balances hold steady."
        ),
        seat_feedback=feedback,
        scores=prior,
        raw_llm_response="",
        used_fallback=True,
    )


class DMService:
    def __init__(self, llm: LLMClient):
        self._llm = llm

    async def adjudicate(
        self,
        *,
        turn_number: int,
        current_scores: TurnScores,
        moves: dict[str, str],
        model: str = DEFAULT_DM_MODEL,
        temperature: float | None = 0.4,
    ) -> DMResult:
        system, user = build_dm_prompt(
            turn_number=turn_number,
            narrative_date=narrative_date_for_turn(turn_number),
            current_scores=current_scores,
            moves=moves,
        )

        raw = ""
        for attempt in range(2):
            try:
                out = await self._llm.complete(
                    model,
                    user,
                    system=system,
                    temperature=temperature,
                    response_format="json",
                    max_tokens=2000,
                )
                raw = out.content
                data = _extract_json(raw)
                scores = normalize_turn_scores(_parse_scores(data["scores"]))
                feedback = {
                    role: str(data["seat_feedback"].get(role, ""))
                    for role in SCORED_ROLES
                }
                # ensure keys exist for humanity/rogue/defender
                return DMResult(
                    world_narrative=str(data["world_narrative"]),
                    seat_feedback=feedback,
                    scores=scores,
                    raw_llm_response=raw,
                    used_fallback=False,
                )
            except (LLMClientError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                logger.warning("DM adjudication attempt %s failed: %s", attempt + 1, exc)
                last_err = str(exc)

        return fallback_result(current_scores, last_err)
