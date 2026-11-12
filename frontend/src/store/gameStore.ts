import { create } from "zustand";
import type {
  Adjudication,
  CategoryScores,
  Game,
  OffAskResult,
  ScoreDeltas,
  SeatConfig,
} from "../api/client";
import * as api from "../api/client";
import { buildDefaultSeats } from "../components/SetupForm";
import { t, useLocaleStore } from "../i18n";

type Screen = "setup" | "game";

interface GameState {
  screen: Screen;
  seats: SeatConfig[];
  game: Game | null;
  viewedTurn: number;
  viewedScores: Record<string, CategoryScores> | null;
  /** Change in viewedScores versus the turn before it (null at the baseline). */
  viewedDeltas: ScoreDeltas | null;
  lastAdjudication: Adjudication | null;
  lastOffReply: OffAskResult | null;
  lastRejection: string | null;
  moveDraft: string;
  moveSubmitted: boolean;
  resolving: boolean;
  error: string | null;
  setSeats: (seats: SeatConfig[]) => void;
  setMoveDraft: (text: string) => void;
  clearError: () => void;
  startGame: () => Promise<void>;
  submitAndResolve: () => Promise<void>;
  viewTurn: (turn: number) => Promise<void>;
  backToSetup: () => void;
}

function maxViewableTurn(game: Game): number {
  return Math.max(game.current_turn, 1);
}

export const useGameStore = create<GameState>((set, get) => ({
  screen: "setup",
  seats: buildDefaultSeats(),
  game: null,
  viewedTurn: 1,
  viewedScores: null,
  viewedDeltas: null,
  lastAdjudication: null,
  lastOffReply: null,
  lastRejection: null,
  moveDraft: "",
  moveSubmitted: false,
  resolving: false,
  error: null,

  setSeats: (seats) => set({ seats }),

  setMoveDraft: (text) => set({ moveDraft: text.slice(0, 800) }),
  clearError: () => set({ error: null }),

  startGame: async () => {
    set({ error: null, resolving: true });
    try {
      const game = await api.createGame(
        get().seats,
        useLocaleStore.getState().locale,
      );
      set({
        game,
        screen: "game",
        viewedTurn: 1,
        viewedScores: game.current_scores,
        viewedDeltas: null,
        lastAdjudication: null,
        lastOffReply: null,
        lastRejection: null,
        moveDraft: "",
        moveSubmitted: false,
        resolving: false,
      });
    } catch (err) {
      set({
        resolving: false,
        error: err instanceof Error ? err.message : t("error.createGame"),
      });
    }
  },

  viewTurn: async (turn: number) => {
    const { game } = get();
    if (!game) return;
    const max = maxViewableTurn(game);
    const target = Math.min(Math.max(turn, 1), max);
    const humanRole =
      game.seats.find((s) => s.player_type === "human" && s.role !== "narrator")
        ?.role ?? "hwg";
    const isCurrent =
      target === game.current_turn && game.status !== "ended";
    const isEndedCurrent =
      target === game.current_turn && game.status === "ended";

    set({ error: null, resolving: true, lastOffReply: null, lastRejection: null });
    try {
      // Turn 1 always shows the Narrator intro + initial scores.
      if (target === 1) {
        const [baseline, turn1] = await Promise.all([
          api.getTurn(game.id, 0),
          api.getTurn(game.id, 1),
        ]);
        const humanMove =
          turn1.moves.find((m) => m.seat_role === humanRole)?.move_text ?? "";
        set({
          viewedTurn: 1,
          viewedScores: baseline.scores ?? game.current_scores,
          viewedDeltas: null,
          lastAdjudication: null,
          moveDraft: isCurrent ? "" : humanMove,
          resolving: false,
        });
        return;
      }

      // Ended on this turn: show that turn's own adjudication.
      if (isEndedCurrent) {
        const data = await api.getTurn(game.id, target);
        const humanMove =
          data.moves.find((m) => m.seat_role === humanRole)?.move_text ?? "";
        set({
          viewedTurn: target,
          viewedScores: data.scores ?? game.current_scores,
          viewedDeltas: data.deltas ?? null,
          lastAdjudication: data.adjudication,
          moveDraft: humanMove,
          resolving: false,
        });
        return;
      }

      // Otherwise: scores + narrative from the prior resolved month
      // (arrival into this turn), dated as this turn in the UI.
      const [prior, data] = await Promise.all([
        api.getTurn(game.id, target - 1),
        api.getTurn(game.id, target),
      ]);
      const humanMove =
        data.moves.find((m) => m.seat_role === humanRole)?.move_text ?? "";
      set({
        viewedTurn: target,
        viewedScores: prior.scores ?? game.current_scores,
        viewedDeltas: prior.deltas ?? null,
        lastAdjudication: prior.adjudication,
        moveDraft: isCurrent ? "" : humanMove,
        resolving: false,
      });
    } catch (err) {
      set({
        resolving: false,
        error: err instanceof Error ? err.message : t("error.resolveTurn"),
      });
    }
  },

  submitAndResolve: async () => {
    const { game, moveDraft, viewedTurn } = get();
    if (!game || !moveDraft.trim()) return;

    const locale = useLocaleStore.getState().locale;
    const isCurrent =
      viewedTurn === game.current_turn && game.status !== "ended";
    const isReplay = !isCurrent;

    if (api.isOffDraft(moveDraft)) {
      if (isReplay) {
        set({ resolving: false, error: t("error.offAsk") });
        return;
      }
      set({ error: null, resolving: true });
      try {
        const reply = await api.askOff(
          game.id,
          game.current_turn,
          moveDraft.trim(),
          locale,
        );
        set({
          lastOffReply: reply,
          lastRejection: null,
          moveDraft: "",
          resolving: false,
        });
      } catch (err) {
        set({
          resolving: false,
          error: err instanceof Error ? err.message : t("error.offAsk"),
        });
      }
      return;
    }

    const submittedText = moveDraft.trim();
    set({ error: null, resolving: true, moveSubmitted: true, lastRejection: null });
    try {
      if (isReplay) {
        const result = await api.replayTurn(
          game.id,
          viewedTurn,
          submittedText,
          locale,
        );
        if (result.rejected) {
          set({
            game: result.game,
            viewedTurn: result.game.current_turn,
            viewedScores: result.game.current_scores,
            viewedDeltas: null,
            lastRejection:
              result.rejection_reason ?? t("transmission.rejectFallback"),
            lastOffReply: null,
            moveDraft: submittedText,
            moveSubmitted: false,
            resolving: false,
          });
          return;
        }
        const nextTurn = result.game.current_turn;
        const prior =
          nextTurn > viewedTurn
            ? await api.getTurn(game.id, viewedTurn)
            : null;
        set({
          game: result.game,
          viewedTurn: nextTurn,
          viewedScores: result.game.current_scores,
          viewedDeltas: result.turn.deltas ?? null,
          lastAdjudication: prior?.adjudication ?? result.turn.adjudication,
          lastOffReply: null,
          lastRejection: null,
          moveDraft: "",
          moveSubmitted: false,
          resolving: false,
        });
        return;
      }

      const turn = game.current_turn;
      await api.submitMove(game.id, turn, submittedText);
      const result = await api.resolveTurn(game.id, turn, locale);
      if (result.rejected) {
        set({
          game: result.game,
          viewedTurn: result.game.current_turn,
          viewedScores: result.game.current_scores,
          lastRejection:
            result.rejection_reason ?? t("transmission.rejectFallback"),
          lastOffReply: null,
          moveDraft: submittedText,
          moveSubmitted: false,
          resolving: false,
        });
        return;
      }
      set({
        game: result.game,
        viewedTurn: result.game.current_turn,
        viewedScores: result.game.current_scores,
        viewedDeltas: result.turn.deltas ?? null,
        lastAdjudication: result.turn.adjudication,
        lastOffReply: null,
        lastRejection: null,
        moveDraft: "",
        moveSubmitted: false,
        resolving: false,
      });
    } catch (err) {
      set({
        resolving: false,
        moveSubmitted: false,
        error: err instanceof Error ? err.message : t("error.resolveTurn"),
      });
    }
  },

  backToSetup: () =>
    set({
      screen: "setup",
      game: null,
      viewedTurn: 1,
      viewedScores: null,
      viewedDeltas: null,
      lastAdjudication: null,
      lastOffReply: null,
      lastRejection: null,
      moveDraft: "",
      moveSubmitted: false,
      error: null,
    }),
}));
