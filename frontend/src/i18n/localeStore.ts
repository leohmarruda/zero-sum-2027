import { create } from "zustand";
import {
  detectBrowserLocale,
  translate,
  type Interp,
  type Locale,
  type MessageKey,
} from "./messages";

const STORAGE_KEY = "zero-sum-2027.locale";

function readStoredLocale(): Locale | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw === "en-US" || raw === "pt-BR") return raw;
  } catch {
    /* ignore */
  }
  return null;
}

function applyDocumentLang(locale: Locale) {
  if (typeof document !== "undefined") {
    document.documentElement.lang = locale;
  }
}

interface LocaleState {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: MessageKey, vars?: Interp) => string;
}

const initial = readStoredLocale() ?? detectBrowserLocale();
applyDocumentLang(initial);

export const useLocaleStore = create<LocaleState>((set, get) => ({
  locale: initial,
  setLocale: (locale) => {
    try {
      localStorage.setItem(STORAGE_KEY, locale);
    } catch {
      /* ignore */
    }
    applyDocumentLang(locale);
    set({ locale });
  },
  t: (key, vars) => translate(get().locale, key, vars),
}));

export function t(key: MessageKey, vars?: Interp): string {
  return useLocaleStore.getState().t(key, vars);
}
