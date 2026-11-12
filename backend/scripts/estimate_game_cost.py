"""Estimate USD cost of a full 60-turn game via llmcall dry_run.

Per turn (MVP): 2 AI seat moves (rogue + defender) + 1 DM adjudication.
Humanity is human — no LLM call for that seat.

Method:
1. dry_run each call type once to count input tokens (no API spend).
2. Price tokens with llmcall.get_model_info rates (openai/gpt-4o-mini
   pricing; openrouter id often lacks a litellm cost map entry).
3. Assume typical completion sizes and multiply by turn count.

Context modes (Narrator user prompt):
- flat: no prior digest (turn-1 shape; schema still requests a digest field).
- raw_history: append prior world narratives for turns 1..N-1 (O(turn)
  input growth → O(T²) game cost) — anti-pattern for comparison only.
- digest: production path — rolling ~300-token world-state digest as prior.

Production uses digest mode. Gate A baseline is O(T); use --compare to
show why raw_history would be O(T²).
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from typing import Literal

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

# ~280–320 tokens — stand-in for a real Narrator world_narrative length.
_PRIOR_NARRATIVE_TEMPLATE = (
    "Turn {n} ({date}): Public world outcome. Export-control coalitions "
    "publish a coordinated licensing list for advanced accelerators; "
    "compliance is uneven and grey-market brokers reroute shipments through "
    "permissive jurisdictions within weeks. Covert compute build-outs "
    "continue in friendly data-center parks, masked as ordinary cloud "
    "expansion; utility filings and land permits are the only weak signals. "
    "Defender-aligned auditors throttle suspicious chip orders and force "
    "re-exports into slower queues, buying months rather than stopping the "
    "flow. HWG convenings produce lab-safety communiqués and dual-use "
    "reporting norms that look strong on paper; private exceptions and "
    "national carve-outs blunt enforcement. Markets price a slow multipolar "
    "compute race: no single polity or AI faction dominates absolute share "
    "this month, but influence and compute edge drift with each contested "
    "supply node. Civil society notices the rhetoric more than the hardware. "
    "No GREYS-scale biosphere threat is confirmed; environmental monitors "
    "flag routine industrial incidents only. Settled facts for later turns: "
    "treat this month's public outcome as already published."
)

# ~300 tokens — stand-in for a rewritten rolling world-state digest.
_WORLD_STATE_DIGEST = """\
World-state digest (rolling, rewrite each turn; keep under ~400 tokens):
Compute race remains multipolar. Covert clusters grow in permissive
jurisdictions; export controls and supply-chain audits slow but do not
stop dual-use chip flows. Human polity coordination is uneven; lab-safety
norms are public theater with private exceptions. No GREYS-scale biosphere
threat confirmed. Open rivalries: Selfish AI vs Defender AI over compute
and influence; HWG pushes standards without hard enforcement. Scores drift
gradually; no seat has a locked win path yet. Public narrative continuity:
treat the digest as ground truth for prior months — do not re-litigate
settled events unless a seat's move credibly revisits them.
"""

ContextMode = Literal["flat", "raw_history", "digest"]


@dataclass
class CallEstimate:
    kind: str
    input_tokens: int
    output_tokens_assumed: int
    cost_usd_per_call: float


def _input_tokens(model: str, system: str, user: str, *, response_format: str) -> int:
    from llmcall import CallConstraints, call

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
    from llmcall import get_model_info

    info = get_model_info(PRICING_MODEL)
    if info is None:
        raise RuntimeError(f"no pricing info for {PRICING_MODEL}")
    return (
        (input_tokens / 1000.0) * info.input_cost_per_1k_tokens
        + (output_tokens / 1000.0) * info.output_cost_per_1k_tokens
    )


def _synthetic_prior_history(through_turn: int) -> str:
    """Concatenate fake public narratives for turns 1..through_turn inclusive."""
    if through_turn < 1:
        return ""
    lines = [
        _PRIOR_NARRATIVE_TEMPLATE.format(
            n=n, date=narrative_date_for_turn(n)
        )
        for n in range(1, through_turn + 1)
    ]
    return "Prior public world narratives (oldest → newest):\n" + "\n".join(lines)


def _attach_narrator_context(
    user: str, *, turn_number: int, context_mode: ContextMode
) -> str:
    """Only used for raw_history anti-pattern samples; digest goes via prompt builder."""
    if context_mode != "raw_history":
        return user
    prior = _synthetic_prior_history(turn_number - 1)
    if not prior:
        return user
    return f"{prior}\n\n{user}"


def _quadratic_game_cost_from_per_turn_samples(
    *,
    cost_at_turn: dict[int, float],
    turns: int,
) -> float:
    """Trapezoid-sum O(T²) path when cost grows roughly linearly with turn.

    Uses measured samples (e.g. turn 1 and turn 55) and interpolates
    linearly for missing turns; extrapolates beyond the last sample.
    """
    samples = sorted(cost_at_turn.items())
    if not samples:
        return 0.0
    total = 0.0
    for t in range(1, turns + 1):
        if t in cost_at_turn:
            total += cost_at_turn[t]
            continue
        # linear interpolate / extrapolate between nearest samples
        below = [(k, v) for k, v in samples if k <= t]
        above = [(k, v) for k, v in samples if k >= t]
        if below and above:
            (t0, c0), (t1, c1) = below[-1], above[0]
            if t1 == t0:
                total += c0
            else:
                frac = (t - t0) / (t1 - t0)
                total += c0 + frac * (c1 - c0)
        elif below:
            t0, c0 = below[-1]
            t1, c1 = samples[-1]
            if len(samples) >= 2:
                t_prev, c_prev = samples[-2]
                slope = (c1 - c_prev) / (t1 - t_prev)
                total += c1 + slope * (t - t1)
            else:
                total += c0
        else:
            total += above[0][1]
    return total


def estimate_full_game(
    *,
    turns: int = 60,
    model: str = RUNTIME_MODEL,
    sample_turn: int = 1,
    context_mode: ContextMode = "flat",
) -> dict:
    roles = ("hwg", "defender_ai", "selfish_ai")
    scores = initial_scores(roles)
    date = narrative_date_for_turn(sample_turn)
    sample_moves = {
        "selfish_ai": "Expand covert compute clusters in friendly jurisdictions.",
        "defender_ai": "Audit supply chains and throttle suspicious chip orders.",
        "hwg": "Coordinate export controls and lab safety standards.",
    }

    per_call: list[CallEstimate] = []
    for role in ("selfish_ai", "defender_ai"):
        system, user = build_seat_move_prompt(
            role=role,
            turn_number=sample_turn,
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

    prior_digest = None
    if context_mode == "digest" and sample_turn > 1:
        prior_digest = _WORLD_STATE_DIGEST
    system, user = build_dm_prompt(
        turn_number=sample_turn,
        narrative_date=date,
        current_scores=scores,
        moves=sample_moves,
        scored_roles=roles,
        prior_world_state_digest=prior_digest,
    )
    user = _attach_narrator_context(
        user, turn_number=sample_turn, context_mode=context_mode
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
    # Naive: assume every turn looks like sample_turn (wrong for raw_history).
    naive_total = cost_per_turn * turns

    from llmcall import get_model_info

    info = get_model_info(PRICING_MODEL)
    return {
        "runtime_model": model,
        "pricing_model": PRICING_MODEL,
        "pricing_input_per_1k_usd": info.input_cost_per_1k_tokens if info else None,
        "pricing_output_per_1k_usd": info.output_cost_per_1k_tokens if info else None,
        "turns": turns,
        "sample_turn": sample_turn,
        "context_mode": context_mode,
        "calls_per_turn": len(per_call),
        "total_calls": len(per_call) * turns,
        "per_call": [asdict(c) for c in per_call],
        "estimated_cost_usd_per_turn": round(cost_per_turn, 6),
        "estimated_cost_usd_input_only_per_turn": round(input_only_per_turn, 6),
        # Alias kept for Gate A test + docs; equals naive sample×turns.
        "estimated_cost_usd_full_game": round(naive_total, 6),
        "estimated_cost_usd_full_game_naive_flat": round(naive_total, 6),
        "assumed_seat_output_tokens": ASSUMED_SEAT_OUTPUT_TOKENS,
        "assumed_dm_output_tokens": ASSUMED_DM_OUTPUT_TOKENS,
        "note": (
            "Input tokens from llmcall dry_run (no API). Output tokens assumed. "
            "USD rates from litellm model info for openai/gpt-4o-mini "
            "(openrouter twin often missing from cost map). "
            "full_game multiplies this sample_turn cost by `turns` — correct for "
            "flat/digest; for raw_history use --compare (O(T²) interpolate)."
        ),
    }


def compare_context_scaling(
    *, turns: int = 60, model: str = RUNTIME_MODEL, late_turn: int = 55
) -> dict:
    """dry_run flat vs raw_history vs digest at turn 1 and late_turn."""
    modes: list[ContextMode] = ["flat", "raw_history", "digest"]
    sample_turns = (1, late_turn)
    reports: dict[str, dict] = {}
    for mode in modes:
        for t in sample_turns:
            key = f"{mode}_t{t}"
            reports[key] = estimate_full_game(
                turns=turns, model=model, sample_turn=t, context_mode=mode
            )

    # O(T²) path for raw_history: interpolate between t=1 and t=late_turn costs
    raw_costs = {
        1: reports["raw_history_t1"]["estimated_cost_usd_per_turn"],
        late_turn: reports[f"raw_history_t{late_turn}"][
            "estimated_cost_usd_per_turn"
        ],
    }
    raw_quadratic = _quadratic_game_cost_from_per_turn_samples(
        cost_at_turn=raw_costs, turns=turns
    )
    flat_total = reports["flat_t1"]["estimated_cost_usd_full_game_naive_flat"]
    digest_total = reports["digest_t1"]["estimated_cost_usd_full_game_naive_flat"]

    dm_in = {
        key: next(c["input_tokens"] for c in rep["per_call"] if c["kind"] == "dm")
        for key, rep in reports.items()
    }

    return {
        "late_turn": late_turn,
        "turns": turns,
        "dm_input_tokens": dm_in,
        "cost_usd_per_turn_sample": {
            key: rep["estimated_cost_usd_per_turn"] for key, rep in reports.items()
        },
        "full_game_usd": {
            "flat_O1": round(flat_total, 6),
            "digest_O1": round(digest_total, 6),
            "raw_history_if_all_turns_like_t1": reports["raw_history_t1"][
                "estimated_cost_usd_full_game"
            ],
            "raw_history_if_all_turns_like_late": reports[
                f"raw_history_t{late_turn}"
            ]["estimated_cost_usd_full_game"],
            "raw_history_interpolated_O_T2": round(raw_quadratic, 6),
        },
        "dm_input_growth": {
            "raw_history_tokens_per_prior_turn": round(
                (dm_in[f"raw_history_t{late_turn}"] - dm_in["raw_history_t1"])
                / max(late_turn - 1, 1),
                1,
            ),
            "digest_delta_vs_flat_tokens": dm_in["digest_t1"] - dm_in["flat_t1"],
        },
        "verdict": (
            "Production uses a rolling world_state_digest (O(T) cost). "
            "Raw prior narratives grow DM input ~linearly with turn "
            f"(t1→t{late_turn} measured) → full-game ~O(T²). Digest keeps "
            "cost near flat."
        ),
        "samples": reports,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--turns", type=int, default=60)
    parser.add_argument("--model", default=RUNTIME_MODEL)
    parser.add_argument(
        "--sample-turn",
        type=int,
        default=1,
        help="Build prompts as of this turn number (default 1).",
    )
    parser.add_argument(
        "--context-mode",
        choices=("flat", "raw_history", "digest"),
        default="flat",
        help="Narrator context: flat (prod), raw_history, or rolling digest.",
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="dry_run flat/raw_history/digest at turn 1 and --late-turn; show O(T²).",
    )
    parser.add_argument("--late-turn", type=int, default=55)
    args = parser.parse_args()
    if args.compare:
        print(
            json.dumps(
                compare_context_scaling(
                    turns=args.turns, model=args.model, late_turn=args.late_turn
                ),
                indent=2,
            )
        )
    else:
        print(
            json.dumps(
                estimate_full_game(
                    turns=args.turns,
                    model=args.model,
                    sample_turn=args.sample_turn,
                    context_mode=args.context_mode,
                ),
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
