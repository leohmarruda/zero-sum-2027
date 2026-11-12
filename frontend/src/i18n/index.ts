export type { Locale, MessageKey, Interp } from "./messages";
export {
  LOCALES,
  LOCALE_LABELS,
  MESSAGES,
  translate,
  monthLabel,
  roleMessageKey,
  roleDescKey,
  roleStartingKey,
  roleHasDelayedWin,
  detectBrowserLocale,
} from "./messages";
export { useLocaleStore, t } from "./localeStore";

