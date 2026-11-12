import { useState } from "react";
import { createPortal } from "react-dom";
import { LOCALES, LOCALE_LABELS, useLocaleStore } from "../i18n";
import { ConfirmModal } from "./ConfirmModal";
import { SettingsModal } from "./SettingsModal";
import "./StatusBar.css";

export interface TurnNav {
  turn: number;
  /** e.g. "JAN 2027" */
  monthYear: string;
  canPrev: boolean;
  canNext: boolean;
  onPrev: () => void;
  onNext: () => void;
}

interface Props {
  turnNav?: TurnNav;
  turnLabel?: string;
  status: "setup" | "in_progress" | "ended";
  winner?: string | null;
  onSettings?: () => void;
}

function SettingsIcon() {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
    </svg>
  );
}

export function StatusBar({
  turnNav,
  turnLabel,
  status,
  winner,
  onSettings,
}: Props) {
  const t = useLocaleStore((s) => s.t);
  const locale = useLocaleStore((s) => s.locale);
  const setLocale = useLocaleStore((s) => s.setLocale);
  const onSetup = status === "setup";
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [confirmHome, setConfirmHome] = useState(false);

  // Logo -> start page. A game in progress must be confirmed first; on the
  // setup screen (or a finished game) there is nothing to abandon.
  const goHome = (e: { preventDefault: () => void }) => {
    e.preventDefault();
    if (onSetup || !onSettings) return;
    if (status === "ended") onSettings();
    else setConfirmHome(true);
  };

  const pill =
    status === "ended"
      ? winner
        ? t("status.victory", { winner: winner.toUpperCase() })
        : t("status.draw")
      : null;

  return (
    <header className="status-bar">
      <a className="brand" href="/" onClick={goHome} aria-label="Zero Sum 2027">
        <span className="brand-mark" aria-hidden="true" />
        <div className="brand-text">
          <div className="wordmark">
            ZERO SUM <span>2027</span>
          </div>
          <div className="tagline">{t("brand.tagline")}</div>
        </div>
      </a>
      {turnNav ? (
        <div className="turn-nav-bar">
          <button
            type="button"
            className="turn-nav-btn"
            aria-label="Previous turn"
            disabled={!turnNav.canPrev}
            onClick={turnNav.onPrev}
          >
            ‹
          </button>
          <div className="turn-readout">
            <div className="turn-kicker">{t("ledger.turnLabel")}</div>
            <div className="turn-value">
              {String(turnNav.turn).padStart(2, "0")}{" "}
              <span>/ {turnNav.monthYear}</span>
            </div>
          </div>
          <button
            type="button"
            className="turn-nav-btn"
            aria-label="Next turn"
            disabled={!turnNav.canNext}
            onClick={turnNav.onNext}
          >
            ›
          </button>
        </div>
      ) : null}
      <div className="status-spacer" />
      <div className="status-meta">
        {!turnNav ? (
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
        ) : null}
        {turnLabel ? <span>{turnLabel}</span> : null}
        {pill ? <span className={`pill pill-${status}`}>{pill}</span> : null}
        <button
          type="button"
          className="settings-btn"
          aria-label={t("status.settings")}
          title={t("status.settings")}
          aria-haspopup="dialog"
          onClick={() => setSettingsOpen(true)}
        >
          <SettingsIcon />
        </button>
      </div>
      {confirmHome && onSettings
        ? createPortal(
            <ConfirmModal
              title={t("brand.homeTitle")}
              body={t("brand.homeBody")}
              confirmLabel={t("brand.homeConfirm")}
              cancelLabel={t("brand.homeStay")}
              onCancel={() => setConfirmHome(false)}
              onConfirm={() => {
                setConfirmHome(false);
                onSettings();
              }}
            />,
            document.body,
          )
        : null}
      {settingsOpen
        ? createPortal(
            <SettingsModal
              onClose={() => setSettingsOpen(false)}
              onNewGame={onSetup ? undefined : onSettings}
            />,
            document.body,
          )
        : null}
    </header>
  );
}
