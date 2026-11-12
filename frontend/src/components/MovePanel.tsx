import { useEffect, useState } from "react";
import { useLocaleStore } from "../i18n";
import "./MovePanel.css";

interface Props {
  title: string;
  value: string;
  disabled?: boolean;
  resolving?: boolean;
  offMode?: boolean;
  replayMode?: boolean;
  onChange: (value: string) => void;
  onSubmit: () => void;
}

export function MovePanel({
  title,
  value,
  disabled,
  resolving,
  offMode,
  replayMode,
  onChange,
  onSubmit,
}: Props) {
  const t = useLocaleStore((s) => s.t);
  const [elapsedSec, setElapsedSec] = useState(0);
  const canSubmit = !disabled && !resolving && value.trim().length > 0;

  useEffect(() => {
    if (!resolving) {
      setElapsedSec(0);
      return;
    }
    setElapsedSec(0);
    const started = Date.now();
    const id = window.setInterval(() => {
      setElapsedSec(Math.floor((Date.now() - started) / 1000));
    }, 250);
    return () => window.clearInterval(id);
  }, [resolving]);

  const submitLabel = resolving
    ? t("move.resolving", { seconds: elapsedSec })
    : offMode
      ? t("move.offSubmit")
      : replayMode
        ? t("move.replaySubmit")
        : t("move.submit");

  return (
    <section className={`panel move-panel${offMode ? " off-mode" : ""}`}>
      <div className="panel-title">
        <span>{title}</span>
        {offMode ? <span className="off-badge">{t("move.offBadge")}</span> : null}
      </div>
      <textarea
        value={value}
        disabled={disabled || resolving}
        maxLength={800}
        placeholder={t("move.placeholder")}
        onChange={(e) => onChange(e.target.value)}
      />
      <div className="move-meta">
        <span className="char-count">{value.length} / 800</span>
        <button
          type="button"
          className="submit-btn"
          disabled={!canSubmit}
          onClick={onSubmit}
        >
          {submitLabel}
        </button>
      </div>
    </section>
  );
}
