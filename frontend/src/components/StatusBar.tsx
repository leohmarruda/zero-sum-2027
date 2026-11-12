import { LOCALES, LOCALE_LABELS, useLocaleStore } from "../i18n";
import "./StatusBar.css";

interface Props {
  turnLabel?: string;
  status: "setup" | "in_progress" | "ended";
  winner?: string | null;
  onSettings?: () => void;
}

function SettingsIcon() {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
    </svg>
  );
}

export function StatusBar({ turnLabel, status, winner, onSettings }: Props) {
  const t = useLocaleStore((s) => s.t);
  const locale = useLocaleStore((s) => s.locale);
  const setLocale = useLocaleStore((s) => s.setLocale);
  const onSetup = status === "setup";

  const pill =
    status === "ended"
      ? winner
        ? t("status.victory", { winner: winner.toUpperCase() })
        : t("status.draw")
      : status === "in_progress"
        ? t("status.inProgress")
        : null;

  return (
    <header className="status-bar">
      <div className="wordmark">
        ZERO SUM <span>2027</span>
      </div>
      <div className="status-meta">
        <div className="lang-switch" role="group" aria-label="Language">
          {LOCALES.map((code) => (
            <button
              key={code}
              type="button"
              className={`lang-btn${locale === code ? " active" : ""}`}
              aria-pressed={locale === code}
              onClick={() => setLocale(code)}
            >
              {LOCALE_LABELS[code]}
            </button>
          ))}
        </div>
        {turnLabel ? <span>{turnLabel}</span> : null}
        {pill ? <span className={`pill pill-${status}`}>{pill}</span> : null}
        {onSetup ? (
          <span
            className="settings-btn active"
            aria-label={t("status.settings")}
            title={t("status.settings")}
            aria-current="page"
          >
            <SettingsIcon />
          </span>
        ) : onSettings ? (
          <button
            type="button"
            className="settings-btn"
            aria-label={t("status.settings")}
            title={t("status.settings")}
            onClick={onSettings}
          >
            <SettingsIcon />
          </button>
        ) : null}
      </div>
    </header>
  );
}
