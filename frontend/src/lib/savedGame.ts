/** Remembers the running game across page reloads (browser-local only). */
const GAME_KEY = "zero-sum-2027.game-id";
const DRAFT_KEY = "zero-sum-2027.move-draft";

function read(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

function write(key: string, value: string | null): void {
  try {
    if (value === null) localStorage.removeItem(key);
    else localStorage.setItem(key, value);
  } catch {
    /* storage unavailable: persistence is best-effort */
  }
}

export function loadGameId(): string | null {
  return read(GAME_KEY) || null;
}

export function saveGameId(id: string): void {
  write(GAME_KEY, id);
}

/** Forget the game and any unsent draft (new game / abandoned game). */
export function clearSavedGame(): void {
  write(GAME_KEY, null);
  write(DRAFT_KEY, null);
}

interface Draft {
  gameId: string;
  turn: number;
  text: string;
}

export function saveDraft(gameId: string, turn: number, text: string): void {
  if (!text) {
    write(DRAFT_KEY, null);
    return;
  }
  write(DRAFT_KEY, JSON.stringify({ gameId, turn, text } satisfies Draft));
}

export function loadDraft(gameId: string, turn: number): string {
  const raw = read(DRAFT_KEY);
  if (!raw) return "";
  try {
    const d = JSON.parse(raw) as Partial<Draft>;
    return d.gameId === gameId && d.turn === turn && typeof d.text === "string"
      ? d.text
      : "";
  } catch {
    return "";
  }
}
