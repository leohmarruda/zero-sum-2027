import type { SeatConfig } from "../api/client";

/** Matches backend `DEFAULT_TURN_CAP` / Gate A dry_run assumptions. */
export const ESTIMATE_TURN_CAP = 60;

/** Calibrated from `backend/scripts/estimate_game_cost.py` dry_run. */
const ASSUMED_SEAT_INPUT_TOKENS = 400;
const ASSUMED_SEAT_OUTPUT_TOKENS = 350;
const ASSUMED_DM_INPUT_TOKENS = 500;
const ASSUMED_DM_OUTPUT_TOKENS = 900;

/** openai/gpt-4o-mini litellm map rates (USD per 1k tokens). */
const INPUT_USD_PER_1K = 0.00015;
const OUTPUT_USD_PER_1K = 0.0006;

function priceCall(inputTokens: number, outputTokens: number): number {
  return (
    (inputTokens / 1000) * INPUT_USD_PER_1K +
    (outputTokens / 1000) * OUTPUT_USD_PER_1K
  );
}

const SEAT_CALL_USD = priceCall(
  ASSUMED_SEAT_INPUT_TOKENS,
  ASSUMED_SEAT_OUTPUT_TOKENS,
);
const DM_CALL_USD = priceCall(ASSUMED_DM_INPUT_TOKENS, ASSUMED_DM_OUTPUT_TOKENS);

export interface GameCostEstimate {
  aiSeatCallsPerTurn: number;
  callsPerTurn: number;
  totalCalls: number;
  estimatedCostUsd: number;
  turns: number;
}

/** Rough full-game USD cost for AI seats + Narrator across `turns` turns. */
export function estimateGameCost(
  seats: SeatConfig[],
  turns: number = ESTIMATE_TURN_CAP,
): GameCostEstimate {
  const aiSeatCallsPerTurn = seats.filter(
    (s) => s.role !== "narrator" && s.player_type === "ai",
  ).length;
  const callsPerTurn = aiSeatCallsPerTurn + 1; // + Narrator/DM
  const perTurn = aiSeatCallsPerTurn * SEAT_CALL_USD + DM_CALL_USD;
  return {
    aiSeatCallsPerTurn,
    callsPerTurn,
    totalCalls: callsPerTurn * turns,
    estimatedCostUsd: perTurn * turns,
    turns,
  };
}

export function formatUsdEstimate(usd: number): string {
  if (usd < 0.01) return `$${usd.toFixed(3)}`;
  if (usd < 10) return `$${usd.toFixed(2)}`;
  return `$${usd.toFixed(0)}`;
}
