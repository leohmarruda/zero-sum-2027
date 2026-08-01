import "./StatusBar.css";

interface Props {
  turnLabel?: string;
  status: "setup" | "in_progress" | "ended";
  winner?: string | null;
}

const statusCopy = {
  setup: "SETUP",
  in_progress: "EM ANDAMENTO",
  ended: "ENCERRADO",
} as const;

export function StatusBar({ turnLabel, status, winner }: Props) {
  const pill =
    status === "ended"
      ? winner
        ? `VITÓRIA · ${winner.toUpperCase()}`
        : "EMPATE"
      : statusCopy[status];

  return (
    <header className="status-bar">
      <div className="wordmark">
        ZERO SUM <span>2027</span>
      </div>
      <div className="status-meta">
        {turnLabel ? <span>{turnLabel}</span> : null}
        <span className={`pill pill-${status}`}>{pill}</span>
      </div>
    </header>
  );
}
