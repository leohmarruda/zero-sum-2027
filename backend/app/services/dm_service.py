"""Narrator adjudication service — parse structured JSON, fallback on failure."""

from __future__ import annotations

import json
import logging
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from app.domain.scoring import normalize_turn_scores
from app.domain.types import SCORE_CATEGORIES, CategoryScores, ScoredRole, TurnScores
from app.llm.prompts import (
    build_dm_prompt,
    build_epilogue_prompt,
    build_move_gate_prompt,
    build_off_prompt,
    clamp_world_state_digest,
    narrative_date_for_turn,
    normalize_locale,
)
from app.llm.types import LLMClient, LLMClientError

logger = logging.getLogger(__name__)

DEFAULT_DM_MODEL = "openrouter/openai/gpt-4o-mini"

_FALLBACK_NARRATIVE = {
    "en-US": "Global channels glitched ({reason}). Power balances hold steady.",
    "pt-BR": (
        "Os canais globais falharam ({reason}). Os equilibrios de poder "
        "permanecem estaveis."
    ),
}
_FALLBACK_FEEDBACK = {
    "en-US": "Communication failure with the Narrator this month.",
    "pt-BR": "Falha de comunicacao com o Narrator neste mes.",
}
_FALLBACK_OFF = {
    "en-US": (
        "The Narrator channel crackles and goes quiet. "
        "Try your clarifying question again."
    ),
    "pt-BR": (
        "O canal do Narrator crepita e fica em silencio. "
        "Tente sua pergunta esclarecedora de novo."
    ),
}
_FALLBACK_DIGEST = {
    "en-US": "Continuity thin after a Narrator channel glitch; prior public balances hold.",
    "pt-BR": (
        "Continuidade fraca apos falha no canal do Narrator; equilibrios "
        "publicos anteriores se mantêm."
    ),
}
_FALLBACK_REJECT = {
    "en-US": (
        "That proposal is not plausible for a single month given the current "
        "balance of power. Revise and try again."
    ),
    "pt-BR": (
        "Essa proposta nao e plausivel para um unico mes dado o equilibrio "
        "atual de poder. Revise e tente de novo."
    ),
}


@dataclass(frozen=True)
class DMResult:
    world_narrative: str
    seat_feedback: dict[str, str]
    scores: TurnScores
    raw_llm_response: str
    world_state_digest: str = ""
    used_fallback: bool = False


@dataclass(frozen=True)
class OffResult:
    answer: str
    used_fallback: bool = False


@dataclass(frozen=True)
class MoveGateResult:
    accepted: bool
    reason: str
    raw_llm_response: str
    used_fallback: bool = False


def _parse_scores(raw_scores: dict, roles: Sequence[ScoredRole]) -> TurnScores:
    out: TurnScores = {}
    for role in roles:
        block = raw_scores[role]
        out[role] = CategoryScores(
            **{cat: float(block[cat]) for cat in SCORE_CATEGORIES}
        )
    return out


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)
    return json.loads(text)


def fallback_result(
    prior: TurnScores,
    reason: str,
    locale: str | None = None,
    *,
    prior_world_state_digest: str | None = None,
) -> DMResult:
    loc = normalize_locale(locale)
    feedback = {role: _FALLBACK_FEEDBACK[loc] for role in prior}
    digest = clamp_world_state_digest(prior_world_state_digest) or _FALLBACK_DIGEST[loc]
    return DMResult(
        world_narrative=_FALLBACK_NARRATIVE[loc].format(reason=reason),
        seat_feedback=feedback,
        scores=prior,
        raw_llm_response="",
        world_state_digest=digest,
        used_fallback=True,
    )


class DMService:
    def __init__(self, llm: LLMClient):
        self._llm = llm

    async def check_human_move(
        self,
        *,
        role: str,
        turn_number: int,
        current_scores: TurnScores,
        move_text: str,
        display_name: str | None = None,
        model: str = DEFAULT_DM_MODEL,
        temperature: float | None = 0.2,
        locale: str | None = None,
    ) -> MoveGateResult:
        system, user = build_move_gate_prompt(
            role=role,
            turn_number=turn_number,
            narrative_date=narrative_date_for_turn(turn_number),
            current_scores=current_scores,
            move_text=move_text,
            display_name=display_name,
            locale=locale,
        )
        loc = normalize_locale(locale)
        raw = ""
        try:
            out = await self._llm.complete(
                model,
                user,
                system=system,
                temperature=temperature,
                response_format="json",
                max_tokens=400,
            )
            raw = out.content
            data = _extract_json(raw)
            accepted = bool(data.get("accepted", True))
            reason = str(data.get("reason") or "").strip()
            if not accepted and not reason:
                reason = _FALLBACK_REJECT[loc]
            return MoveGateResult(
                accepted=accepted,
                reason=reason,
                raw_llm_response=raw,
                used_fallback=False,
            )
        except (
            LLMClientError,
            KeyError,
            TypeError,
            ValueError,
            json.JSONDecodeError,
        ) as exc:
            logger.warning("Narrator move gate failed: %s", exc)
            # Fail open — do not strand the player on a gate outage.
            return MoveGateResult(
                accepted=True,
                reason="",
                raw_llm_response=raw,
                used_fallback=True,
            )

    async def adjudicate(
        self,
        *,
        turn_number: int,
        current_scores: TurnScores,
        moves: dict[str, str],
        scored_roles: Sequence[str],
        display_names: Mapping[str, str] | None = None,
        model: str = DEFAULT_DM_MODEL,
        temperature: float | None = 0.4,
        locale: str | None = None,
        prior_world_state_digest: str | None = None,
        world_event: str | None = None,
    ) -> DMResult:
        roles = list(scored_roles)
        system, user = build_dm_prompt(
            turn_number=turn_number,
            narrative_date=narrative_date_for_turn(turn_number),
            current_scores=current_scores,
            moves=moves,
            scored_roles=roles,
            display_names=display_names,
            locale=locale,
            prior_world_state_digest=prior_world_state_digest,
            world_event=world_event,
        )

        raw = ""
        last_err = "unknown"
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
                scores = normalize_turn_scores(
                    _parse_scores(data["scores"], roles), roles
                )
                feedback = {
                    role: str(data["seat_feedback"].get(role, "")) for role in roles
                }
                digest = clamp_world_state_digest(data.get("world_state_digest"))
                if not digest:
                    # Soft-missing field: seed from public narrative so continuity
                    # still has something to roll forward next turn.
                    digest = clamp_world_state_digest(data.get("world_narrative"))
                return DMResult(
                    world_narrative=str(data["world_narrative"]),
                    seat_feedback=feedback,
                    scores=scores,
                    raw_llm_response=raw,
                    world_state_digest=digest,
                    used_fallback=False,
                )
            except (
                LLMClientError,
                KeyError,
                TypeError,
                ValueError,
                json.JSONDecodeError,
            ) as exc:
                logger.warning(
                    "Narrator adjudication attempt %s failed: %s", attempt + 1, exc
                )
                last_err = str(exc)

        return fallback_result(
            current_scores,
            last_err,
            locale=locale,
            prior_world_state_digest=prior_world_state_digest,
        )

    async def write_epilogue(
        self,
        *,
        ending: str,
        winner: str | None,
        final_turn: int,
        history: Sequence[TurnScores],
        world_state_digest: str | None,
        display_names: Mapping[str, str] | None = None,
        model: str = DEFAULT_DM_MODEL,
        temperature: float | None = 0.7,
        locale: str | None = None,
    ) -> str | None:
        """One closing call. Returns None on failure — the epilogue is optional."""
        system, user = build_epilogue_prompt(
            ending=ending,
            winner=winner,
            final_turn=final_turn,
            history=history,
            world_state_digest=world_state_digest,
            display_names=display_names,
            locale=locale,
        )
        try:
            out = await self._llm.complete(
                model,
                user,
                system=system,
                temperature=temperature,
                response_format="text",
                max_tokens=700,
            )
        except LLMClientError as exc:
            logger.warning("Narrator epilogue failed: %s", exc)
            return None
        return out.content.strip() or None

    async def answer_off(
        self,
        *,
        role: str,
        turn_number: int,
        current_scores: TurnScores,
        question: str,
        prior_world_narrative: str | None = None,
        prior_world_state_digest: str | None = None,
        prior_feedback: str | None = None,
        display_name: str | None = None,
        model: str = DEFAULT_DM_MODEL,
        temperature: float | None = 0.3,
        locale: str | None = None,
    ) -> OffResult:
        system, user = build_off_prompt(
            role=role,
            turn_number=turn_number,
            narrative_date=narrative_date_for_turn(turn_number),
            current_scores=current_scores,
            question=question,
            prior_world_narrative=prior_world_narrative,
            prior_world_state_digest=prior_world_state_digest,
            prior_feedback=prior_feedback,
            display_name=display_name,
            locale=locale,
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
            answer = out.content.strip()
            if not answer:
                raise LLMClientError("empty", "empty /off answer")
            return OffResult(answer=answer, used_fallback=False)
        except LLMClientError as exc:
            logger.warning("Narrator /off failed: %s", exc)
            loc = normalize_locale(locale)
            return OffResult(
                answer=_FALLBACK_OFF[loc],
                used_fallback=True,
            )
