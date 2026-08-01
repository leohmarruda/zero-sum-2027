"""Estimate USD cost of a full 60-turn game via llmcall dry_run.

Per turn (MVP): 2 AI seat moves (rogue + defender) + 1 DM adjudication.
Humanity is human — no LLM call for that seat.

Method:
1. dry_run each call type once to count input tokens (no API spend).
2. Price tokens with llmcall.get_model_info rates (openai/gpt-4o-mini
   pricing; openrouter id often lacks a litellm cost map entry).
3. Assume typical completion sizes and multiply by turn count.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass

from llmcall import CallConstraints, call, get_model_info

from app.domain.scoring import initial_scores
from app.llm.prompts import (
    build_dm_prompt,
    build_seat_move_prompt,
    narrative_date_for_turn,
)

# Runtime model id (OpenRouter). Pricing falls back to the OpenAI twin.
RUNTIME_MODEL = "openrouter/openai/gpt-4o-mini"
PRICING_MODEL = "openai/gpt-4o-mini"

ASSUMED_SEAT_OUTPUT_TOKENS = 350
ASSUMED_DM_OUTPUT_TOKENS = 900


@dataclass
class CallEstimate:
    kind: str
    input_tokens: int
    output_tokens_assumed: int
    cost_usd_per_call: float


def _input_tokens(model: str, system: str, user: str, *, response_format: str) -> int:
    result = call(
        model,
        user,
        system=system,
        constraints=CallConstraints(response_format=response_format),  # type: ignore[arg-type]
        dry_run=True,
    )
    if hasattr(result, "error_type"):
        raise RuntimeError(f"dry_run failed: {result}")
    return int(result.input_tokens)


def _price(input_tokens: int, output_tokens: int) -> float:
    info = get_model_info(PRICING_MODEL)
    if info is None:
        raise RuntimeError(f"no pricing info for {PRICING_MODEL}")
    return (
        (input_tokens / 1000.0) * info.input_cost_per_1k_tokens
        + (output_tokens / 1000.0) * info.output_cost_per_1k_tokens
    )


def estimate_full_game(*, turns: int = 60, model: str = RUNTIME_MODEL) -> dict:
    scores = initial_scores()
    date = narrative_date_for_turn(1)
    sample_moves = {
        "rogue_ai": "Expand covert compute clusters in friendly jurisdictions.",
        "defender_ai": "Audit supply chains and throttle suspicious chip orders.",
        "humanity": "Coordinate export controls and lab safety standards.",
    }

    per_call: list[CallEstimate] = []
    for role in ("rogue_ai", "defender_ai"):
        system, user = build_seat_move_prompt(
            role=role,
            turn_number=1,
            narrative_date=date,
            current_scores=scores,
            prior_feedback="Hold the line.",
        )
        in_tok = _input_tokens(model, system, user, response_format="text")
        per_call.append(
            CallEstimate(
                kind=f"seat:{role}",
                input_tokens=in_tok,
                output_tokens_assumed=ASSUMED_SEAT_OUTPUT_TOKENS,
                cost_usd_per_call=_price(in_tok, ASSUMED_SEAT_OUTPUT_TOKENS),
            )
        )

    system, user = build_dm_prompt(
        turn_number=1,
        narrative_date=date,
        current_scores=scores,
        moves=sample_moves,
    )
    in_tok = _input_tokens(model, system, user, response_format="json")
    per_call.append(
        CallEstimate(
            kind="dm",
            input_tokens=in_tok,
            output_tokens_assumed=ASSUMED_DM_OUTPUT_TOKENS,
            cost_usd_per_call=_price(in_tok, ASSUMED_DM_OUTPUT_TOKENS),
        )
    )

    cost_per_turn = sum(c.cost_usd_per_call for c in per_call)
    input_only_per_turn = sum(_price(c.input_tokens, 0) for c in per_call)
    total = cost_per_turn * turns

    info = get_model_info(PRICING_MODEL)
    return {
        "runtime_model": model,
        "pricing_model": PRICING_MODEL,
        "pricing_input_per_1k_usd": info.input_cost_per_1k_tokens if info else None,
        "pricing_output_per_1k_usd": info.output_cost_per_1k_tokens if info else None,
        "turns": turns,
        "calls_per_turn": len(per_call),
        "total_calls": len(per_call) * turns,
        "per_call": [asdict(c) for c in per_call],
        "estimated_cost_usd_per_turn": round(cost_per_turn, 6),
        "estimated_cost_usd_input_only_per_turn": round(input_only_per_turn, 6),
        "estimated_cost_usd_full_game": round(total, 6),
        "assumed_seat_output_tokens": ASSUMED_SEAT_OUTPUT_TOKENS,
        "assumed_dm_output_tokens": ASSUMED_DM_OUTPUT_TOKENS,
        "note": (
            "Input tokens from llmcall dry_run (no API). Output tokens assumed. "
            "USD rates from litellm model info for openai/gpt-4o-mini "
            "(openrouter twin often missing from cost map)."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--turns", type=int, default=60)
    parser.add_argument("--model", default=RUNTIME_MODEL)
    args = parser.parse_args()
    print(json.dumps(estimate_full_game(turns=args.turns, model=args.model), indent=2))


if __name__ == "__main__":
    main()
