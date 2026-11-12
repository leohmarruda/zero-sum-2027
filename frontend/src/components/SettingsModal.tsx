import { useEffect, useId, useState } from "react";
import { LOCALES, LOCALE_LABELS, useLocaleStore, type MessageKey } from "../i18n";
import {
  API_KEY_PROVIDERS,
  loadApiKeys,
  saveApiKeys,
  type ApiKeyProvider,
  type ApiKeys,
} from "../lib/apiKeys";
import "./SetupForm.css";
import "./SettingsModal.css";

const KEY_LABELS: Record<ApiKeyProvider, MessageKey> = {
  openrouter: "settings.keyOpenrouter",
  openai: "settings.keyOpenai",
  anthropic: "settings.keyAnthropic",
};

interface Props {
  onClose: () => void;
  /** Present only inside a running game: abandon it and return to setup. */
  onNewGame?: () => void;
}

export function SettingsModal({ onClose, onNewGame }: Props) {
  const t = useLocaleStore((s) => s.t);
  const locale = useLocaleStore((s) => s.locale);
  const setLocale = useLocaleStore((s) => s.setLocale);
  const titleId = useId();
  const [drafts, setDrafts] = useState<ApiKeys>(() => loadApiKeys());
  const [revealed, setRevealed] = useState<Partial<Record<ApiKeyProvider, boolean>>>({});
  const [saveFailed, setSaveFailed] = useState(false);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const save = () => {
    if (saveApiKeys(drafts)) {
      onClose();
    } else {
      setSaveFailed(true);
    }
  };

  const hasAnyDraft = API_KEY_PROVIDERS.some((p) => drafts[p]?.trim());

  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <div
        className="modal settings-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 id={titleId} className="modal-title">
          {t("settings.title")}
          <button
            type="button"
            className="modal-close"
            aria-label={t("settings.cancel")}
            onClick={onClose}
          >
            ✕
          </button>
        </h2>

        <section className="settings-section">
          <div className="settings-label">{t("settings.language")}</div>
          <div className="lang-switch" role="group" aria-label={t("settings.language")}>
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
        </section>

        <section className="settings-section">
          <div className="settings-label">{t("settings.apiKeys")}</div>
          <p className="settings-hint">{t("settings.apiKeysHint")}</p>
          {API_KEY_PROVIDERS.map((provider) => (
            <label className="modal-field" key={provider}>
              <span className="settings-key-name">{t(KEY_LABELS[provider])}</span>
              <span className="settings-key-row">
                <input
                  type={revealed[provider] ? "text" : "password"}
                  value={drafts[provider] ?? ""}
                  autoComplete="off"
                  spellCheck={false}
                  placeholder="sk-…"
                  onChange={(e) =>
                    setDrafts((d) => ({ ...d, [provider]: e.target.value }))
                  }
                />
                <button
                  type="button"
                  className="modal-btn ghost"
                  onClick={() =>
                    setRevealed((r) => ({ ...r, [provider]: !r[provider] }))
                  }
                >
                  {revealed[provider] ? t("settings.hide") : t("settings.show")}
                </button>
              </span>
            </label>
          ))}
          {saveFailed ? (
            <p className="settings-error" role="alert">
              {t("settings.storageFail")}
            </p>
          ) : null}
        </section>

        <div className="modal-actions">
          <div className="settings-side-actions">
            {hasAnyDraft ? (
              <button type="button" className="linkish danger" onClick={() => setDrafts({})}>
                {t("settings.clearKeys")}
              </button>
            ) : null}
            {onNewGame ? (
              <button
                type="button"
                className="modal-btn ghost"
                onClick={() => {
                  onClose();
                  onNewGame();
                }}
              >
                {t("settings.newGame")}
              </button>
            ) : null}
          </div>
          <div className="modal-actions-end">
            <button type="button" className="modal-btn ghost" onClick={onClose}>
              {t("settings.cancel")}
            </button>
            <button type="button" className="modal-btn primary" onClick={save}>
              {t("settings.save")}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
