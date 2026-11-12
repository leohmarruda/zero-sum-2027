import { useEffect, useState } from "react";
import { useLocaleStore } from "../i18n";
import "./TransmissionPanel.css";

interface Props {
  turnNumber?: number;
  headLabel?: string;
  dateLabel?: string;
  narrative: string;
  feedback?: string | null;
  feedbackSeatLabel?: string;
  question?: string | null;
}

/** Reveals `text` quickly, character by character (whole thing in ~1.5s max). */
function useTypewriter(text: string) {
  const reduced =
    typeof window !== "undefined" &&
    typeof window.matchMedia === "function" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const [count, setCount] = useState(reduced ? text.length : 0);

  useEffect(() => {
    if (reduced) {
      setCount(text.length);
      return;
    }
    setCount(0);
    const step = Math.max(2, Math.ceil(text.length / 100));
    const id = window.setInterval(() => {
      setCount((c) => {
        const next = Math.min(c + step, text.length);
        if (next >= text.length) window.clearInterval(id);
        return next;
      });
    }, 15);
    return () => window.clearInterval(id);
  }, [text, reduced]);

  return { count, done: count >= text.length, finish: () => setCount(text.length) };
}

export function TransmissionPanel({
  turnNumber,
  headLabel,
  dateLabel,
  narrative,
  feedback,
  feedbackSeatLabel,
  question,
}: Props) {
  const t = useLocaleStore((s) => s.t);
  const typed = useTypewriter(narrative);
  const head =
    headLabel ??
    t("transmission.head", {
      turn: String(turnNumber ?? 0).padStart(2, "0"),
    });
  return (
    <section className="panel transmission" onClick={typed.finish}>
      <div className="transmission-head">
        <span>{head}</span>
        {dateLabel ? <span>{dateLabel}</span> : null}
      </div>
      {question ? (
        <div className="transmission-question">
          <b>{t("transmission.offQuestion")}</b> {question}
        </div>
      ) : null}
      <div className="transmission-body">
        <span className="sr-only">{narrative}</span>
        <span aria-hidden="true">
          {narrative.slice(0, typed.count)}
          {typed.done ? null : <span className="typing-cursor" />}
          <span className="typing-rest">{narrative.slice(typed.count)}</span>
        </span>
      </div>
      {feedback && typed.done ? (
        <div className="transmission-feedback">
          <b>
            {t("transmission.feedbackLabel", {
              seat: feedbackSeatLabel ?? t("role.hwg"),
            })}
          </b>{" "}
          {feedback}
        </div>
      ) : null}
    </section>
  );
}
