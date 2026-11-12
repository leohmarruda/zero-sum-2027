import { apiKeyHeaders } from "../lib/apiKeys";

export type PlayableRole =
  | "paperclip_max"
  | "selfish_ai"
  | "paternalistic_ai"
  | "defender_ai"
  | "exterminator_ai"
  | "hwg"
  | "us"
  | "china"
  | "eu"
  | "het"
  | "gray_aliens";

export type SeatRole = PlayableRole | "narrator";
export type ScoredRole = string;
export type PlayerType = "human" | "ai";
export type GameStatus = "setup" | "in_progress" | "ended";

export const PLAYABLE_ROLES: PlayableRole[] = [
  "paperclip_max",
  "selfish_ai",
  "paternalistic_ai",
  "defender_ai",
  "exterminator_ai",
  "hwg",
  "us",
  "china",
  "eu",
  "het",
  "gray_aliens",
];

export const DEFAULT_PLAYABLE_ROLES: PlayableRole[] = [
  "hwg",
  "defender_ai",
  "selfish_ai",
];

export const ROLE_CSS: Record<SeatRole, string> = {
  paperclip_max: "paperclip",
  selfish_ai: "selfish",
  paternalistic_ai: "paternalistic",
  defender_ai: "defender",
  exterminator_ai: "exterminator",
  hwg: "hwg",
  us: "us",
  china: "china",
  eu: "eu",
  het: "het",
  gray_aliens: "aliens",
  narrator: "narrator",
};

export const ROLE_SHORT: Record<PlayableRole, string> = {
  paperclip_max: "PMAX",
  selfish_ai: "SA",
  paternalistic_ai: "PAI",
  defender_ai: "DAI",
  exterminator_ai: "EAI",
  hwg: "HWG",
  us: "US",
  china: "CN",
  eu: "UE",
  het: "HET",
  gray_aliens: "GREYS",
};

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
  display_name?: string | null;
}

export interface Game {
  id: string;
  status: GameStatus;
  current_turn: number;
  turn_cap: number;
  humanity_win_turn: number;
  winner: string | null;
  ending?: string | null;
  epilogue?: string | null;
  ended_at: string | null;
  seats: SeatConfig[];
  current_scores: Record<string, CategoryScores> | null;
  narrator_intro?: string | null;
}

export interface Move {
  seat_role: SeatRole;
  move_text: string;
  turn_number: number;
}

export interface Adjudication {
  turn_number: number;
  world_narrative: string;
  world_state_digest?: string;
  seat_feedback: Record<string, string>;
}

/** seat role -> category -> signed change versus the previous turn. */
export type ScoreDeltas = Record<string, Record<string, number>>;

export interface TurnView {
  turn_number: number;
  moves: Move[];
  adjudication: Adjudication | null;
  scores: Record<string, CategoryScores> | null;
  deltas?: ScoreDeltas | null;
}

export interface ResolveResult {
  game: Game;
  turn: TurnView;
  already_resolved: boolean;
  rejected?: boolean;
  rejection_reason?: string | null;
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
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...apiKeyHeaders(),
      ...(init?.headers ?? {}),
    },
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err = data?.error ?? {};
    throw new ApiError(err.code ?? "http_error", err.message ?? res.statusText, res.status);
  }
  return data as T;
}

export function createGame(seats?: SeatConfig[], locale?: string) {
  return request<Game>("/games", {
    method: "POST",
    body: JSON.stringify({
      ...(seats ? { seats } : {}),
      ...(locale ? { locale } : {}),
    }),
  });
}

export interface ContentBundle {
  locale: string;
  setup_intro: string;
  narrator_intro_lines: Record<string, string>;
}

export function getContent(locale?: string) {
  const q = locale ? `?locale=${encodeURIComponent(locale)}` : "";
  return request<ContentBundle>(`/content${q}`);
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

export function resolveTurn(gameId: string, turn: number, locale?: string) {
  const q = locale ? `?locale=${encodeURIComponent(locale)}` : "";
  return request<ResolveResult>(
    `/games/${gameId}/turns/${turn}/resolve${q}`,
    { method: "POST" },
  );
}

export function replayTurn(
  gameId: string,
  turn: number,
  moveText: string,
  locale?: string,
) {
  return request<ResolveResult>(`/games/${gameId}/turns/${turn}/replay`, {
    method: "POST",
    body: JSON.stringify({
      move_text: moveText,
      ...(locale ? { locale } : {}),
    }),
  });
}

export interface OffAskResult {
  turn_number: number;
  seat_role: SeatRole;
  question: string;
  answer: string;
}

export function askOff(
  gameId: string,
  turn: number,
  moveText: string,
  locale?: string,
) {
  return request<OffAskResult>(`/games/${gameId}/turns/${turn}/off`, {
    method: "POST",
    body: JSON.stringify({
      move_text: moveText,
      ...(locale ? { locale } : {}),
    }),
  });
}

export function getTurn(gameId: string, turn: number) {
  return request<TurnView>(`/games/${gameId}/turns/${turn}`);
}

/** True when the draft is an /off clarifying question. */
export function isOffDraft(text: string): boolean {
  return /^\s*\/off\b/i.test(text);
}
