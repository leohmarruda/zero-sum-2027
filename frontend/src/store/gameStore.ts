import { create } from "zustand";
import type { Adjudication, Game, SeatConfig } from "../api/client";
import * as api from "../api/client";

const DEFAULT_MODEL = "openrouter/openai/gpt-4o-mini";

export const defaultSeats = (): SeatConfig[] => [
  { role: "humanity", player_type: "human", model: null, temperature: null },
  { role: "rogue_ai", player_type: "ai", model: DEFAULT_MODEL, temperature: 0.7 },
  { role: "defender_ai", player_type: "ai", model: DEFAULT_MODEL, temperature: 0.7 },
  { role: "dm", player_type: "ai", model: DEFAULT_MODEL, temperature: 0.4 },
];

type Screen = "setup" | "game";

interface GameState {
  screen: Screen;
  seats: SeatConfig[];
  game: Game | null;
  lastAdjudication: Adjudication | null;
  moveDraft: string;
  moveSubmitted: boolean;
  resolving: boolean;
  error: string | null;
  setSeatModel: (role: SeatConfig["role"], model: string) => void;
  setSeatTemp: (role: SeatConfig["role"], temperature: number) => void;
  setMoveDraft: (text: string) => void;
  clearError: () => void;
  startGame: () => Promise<void>;
  submitAndResolve: () => Promise<void>;
  backToSetup: () => void;
}

export const useGameStore = create<GameState>((set, get) => ({
  screen: "setup",
  seats: defaultSeats(),
  game: null,
  lastAdjudication: null,
  moveDraft: "",
  moveSubmitted: false,
  resolving: false,
  error: null,

  setSeatModel: (role, model) =>
    set((s) => ({
      seats: s.seats.map((seat) => (seat.role === role ? { ...seat, model } : seat)),
    })),

  setSeatTemp: (role, temperature) =>
    set((s) => ({
      seats: s.seats.map((seat) =>
        seat.role === role ? { ...seat, temperature } : seat,
      ),
    })),

  setMoveDraft: (text) => set({ moveDraft: text.slice(0, 800) }),
  clearError: () => set({ error: null }),

  startGame: async () => {
    set({ error: null, resolving: true });
    try {
      const game = await api.createGame(get().seats);
      set({
        game,
        screen: "game",
        lastAdjudication: null,
        moveDraft: "",
        moveSubmitted: false,
        resolving: false,
      });
    } catch (err) {
      set({
        resolving: false,
        error: err instanceof Error ? err.message : "Falha ao criar partida",
      });
    }
  },

  submitAndResolve: async () => {
    const { game, moveDraft } = get();
    if (!game || !moveDraft.trim()) return;
    set({ error: null, resolving: true, moveSubmitted: true });
    try {
      const turn = game.current_turn;
      await api.submitMove(game.id, turn, moveDraft.trim());
      const result = await api.resolveTurn(game.id, turn);
      set({
        game: result.game,
        lastAdjudication: result.turn.adjudication,
        moveDraft: "",
        moveSubmitted: false,
        resolving: false,
      });
    } catch (err) {
      set({
        resolving: false,
        moveSubmitted: false,
        error: err instanceof Error ? err.message : "Falha ao resolver turno",
      });
    }
  },

  backToSetup: () =>
    set({
      screen: "setup",
      game: null,
      lastAdjudication: null,
      moveDraft: "",
      moveSubmitted: false,
      error: null,
    }),
}));
