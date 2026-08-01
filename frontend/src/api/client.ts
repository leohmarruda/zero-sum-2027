export type SeatRole = "rogue_ai" | "defender_ai" | "dm" | "humanity";
export type ScoredRole = "rogue_ai" | "defender_ai" | "humanity";
export type PlayerType = "human" | "ai";
export type GameStatus = "setup" | "in_progress" | "ended";

export interface CategoryScores {
  sm: number;
  rc: number;
  ic: number;
  pc: number;
  cs: number;
}

export interface SeatConfig {
  role: SeatRole;
  player_type: PlayerType;
  model: string | null;
  temperature: number | null;
}

export interface Game {
  id: string;
  status: GameStatus;
  current_turn: number;
  turn_cap: number;
  humanity_win_turn: number;
  winner: string | null;
  ended_at: string | null;
  seats: SeatConfig[];
  current_scores: Record<ScoredRole, CategoryScores> | null;
}

export interface Move {
  seat_role: SeatRole;
  move_text: string;
  turn_number: number;
}

export interface Adjudication {
  turn_number: number;
  world_narrative: string;
  seat_feedback: Record<string, string>;
}

export interface TurnView {
  turn_number: number;
  moves: Move[];
  adjudication: Adjudication | null;
  scores: Record<ScoredRole, CategoryScores> | null;
}

export interface ResolveResult {
  game: Game;
  turn: TurnView;
  already_resolved: boolean;
}

export class ApiError extends Error {
  code: string;
  status: number;

  constructor(code: string, message: string, status: number) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err = data?.error ?? {};
    throw new ApiError(err.code ?? "http_error", err.message ?? res.statusText, res.status);
  }
  return data as T;
}

export function createGame(seats?: SeatConfig[]) {
  return request<Game>("/games", {
    method: "POST",
    body: JSON.stringify(seats ? { seats } : {}),
  });
}

export function getGame(gameId: string) {
  return request<Game>(`/games/${gameId}`);
}

export function submitMove(gameId: string, turn: number, moveText: string) {
  return request<Move>(`/games/${gameId}/turns/${turn}/moves`, {
    method: "POST",
    body: JSON.stringify({ move_text: moveText }),
  });
}

export function resolveTurn(gameId: string, turn: number) {
  return request<ResolveResult>(`/games/${gameId}/turns/${turn}/resolve`, {
    method: "POST",
  });
}

export function getTurn(gameId: string, turn: number) {
  return request<TurnView>(`/games/${gameId}/turns/${turn}`);
}
