/**
 * User-provided LLM provider keys, kept in this browser only (localStorage) and
 * sent to the game backend as `X-Api-Key-<provider>` headers on each request.
 */

export const API_KEY_PROVIDERS = ["openrouter", "openai", "anthropic"] as const;
export type ApiKeyProvider = (typeof API_KEY_PROVIDERS)[number];
export type ApiKeys = Partial<Record<ApiKeyProvider, string>>;

const STORAGE_KEY = "zero-sum-2027.api-keys";

export function loadApiKeys(): ApiKeys {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw) as Record<string, unknown>;
    const out: ApiKeys = {};
    for (const p of API_KEY_PROVIDERS) {
      const v = parsed[p];
      if (typeof v === "string" && v.trim()) out[p] = v.trim();
    }
    return out;
  } catch {
    return {};
  }
}

/** Persist keys; blank values are dropped. Returns false if storage is unavailable. */
export function saveApiKeys(keys: ApiKeys): boolean {
  const clean: ApiKeys = {};
  for (const p of API_KEY_PROVIDERS) {
    const v = keys[p]?.trim();
    if (v) clean[p] = v;
  }
  try {
    if (Object.keys(clean).length === 0) {
      localStorage.removeItem(STORAGE_KEY);
    } else {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(clean));
    }
    return true;
  } catch {
    return false;
  }
}

export function apiKeyHeaders(keys: ApiKeys = loadApiKeys()): Record<string, string> {
  const headers: Record<string, string> = {};
  for (const p of API_KEY_PROVIDERS) {
    const v = keys[p];
    if (v) headers[`X-Api-Key-${p}`] = v;
  }
  return headers;
}
