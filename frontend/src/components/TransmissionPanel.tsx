import "./TransmissionPanel.css";

interface Props {
  turnNumber: number;
  dateLabel?: string;
  narrative: string;
  feedback?: string | null;
}

export function TransmissionPanel({
  turnNumber,
  dateLabel,
  narrative,
  feedback,
}: Props) {
  return (
    <section className="panel transmission">
      <div className="transmission-head">
        <span>TRANSMISSÃO DM — TURNO {String(turnNumber).padStart(2, "0")}</span>
        {dateLabel ? <span>{dateLabel}</span> : null}
      </div>
      <div className="transmission-body">{narrative}</div>
      {feedback ? (
        <div className="transmission-feedback">
          <b>Relatório para Humanidade:</b> {feedback}
        </div>
      ) : null}
    </section>
  );
}
