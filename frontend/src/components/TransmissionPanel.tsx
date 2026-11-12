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
  const head =
    headLabel ??
    t("transmission.head", {
      turn: String(turnNumber ?? 0).padStart(2, "0"),
    });
  return (
    <section className="panel transmission">
      <div className="transmission-head">
        <span>{head}</span>
        {dateLabel ? <span>{dateLabel}</span> : null}
      </div>
      {question ? (
        <div className="transmission-question">
          <b>{t("transmission.offQuestion")}</b> {question}
        </div>
      ) : null}
      <div className="transmission-body">{narrative}</div>
      {feedback ? (
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
