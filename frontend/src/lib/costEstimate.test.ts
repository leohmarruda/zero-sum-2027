import { describe, expect, it } from "vitest";
import type { SeatConfig } from "../api/client";
import {
  ESTIMATE_TURN_CAP,
  estimateGameCost,
  formatUsdEstimate,
} from "./costEstimate";

const defaultSeats: SeatConfig[] = [
  {
    role: "hwg",
    player_type: "human",
    model: null,
    temperature: null,
  },
  {
    role: "defender_ai",
    player_type: "ai",
    model: "openrouter/openai/gpt-4o-mini",
    temperature: 0.7,
  },
  {
    role: "selfish_ai",
    player_type: "ai",
    model: "openrouter/openai/gpt-4o-mini",
    temperature: 0.7,
  },
  {
    role: "narrator",
    player_type: "ai",
    model: "openrouter/openai/gpt-4o-mini",
    temperature: 0.4,
  },
];

describe("estimateGameCost", () => {
  it("matches Gate A ballpark for the default lineup", () => {
    const est = estimateGameCost(defaultSeats);
    expect(est.turns).toBe(ESTIMATE_TURN_CAP);
    expect(est.aiSeatCallsPerTurn).toBe(2);
    expect(est.callsPerTurn).toBe(3);
    expect(est.totalCalls).toBe(180);
    // Validated dry_run was ~$0.068; heuristic should stay in the same band.
    expect(est.estimatedCostUsd).toBeGreaterThan(0.05);
    expect(est.estimatedCostUsd).toBeLessThan(0.1);
    expect(formatUsdEstimate(est.estimatedCostUsd)).toBe("$0.07");
  });

  it("scales when more AI seats are added", () => {
    const withExtra: SeatConfig[] = [
      ...defaultSeats,
      {
        role: "paperclip_max",
        player_type: "ai",
        model: "openrouter/openai/gpt-4o-mini",
        temperature: 0.7,
      },
    ];
    const base = estimateGameCost(defaultSeats).estimatedCostUsd;
    const more = estimateGameCost(withExtra).estimatedCostUsd;
    expect(more).toBeGreaterThan(base);
  });

  it("treats human seats as free", () => {
    const allHumanPlayable: SeatConfig[] = defaultSeats.map((s) =>
      s.role === "narrator"
        ? s
        : { ...s, player_type: "human" as const, model: null, temperature: null },
    );
    const est = estimateGameCost(allHumanPlayable);
    expect(est.aiSeatCallsPerTurn).toBe(0);
    // Narrator only.
    expect(est.estimatedCostUsd).toBeGreaterThan(0);
    expect(est.estimatedCostUsd).toBeLessThan(
      estimateGameCost(defaultSeats).estimatedCostUsd,
    );
  });
});
