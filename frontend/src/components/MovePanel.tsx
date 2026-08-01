import "./MovePanel.css";

interface Props {
  title: string;
  value: string;
  disabled?: boolean;
  resolving?: boolean;
  onChange: (value: string) => void;
  onSubmit: () => void;
}

export function MovePanel({
  title,
  value,
  disabled,
  resolving,
  onChange,
  onSubmit,
}: Props) {
  const canSubmit = !disabled && !resolving && value.trim().length > 0;

  return (
    <section className="panel move-panel">
      <div className="panel-title">
        <span>{title}</span>
      </div>
      <textarea
        value={value}
        disabled={disabled || resolving}
        maxLength={800}
        placeholder="Descreva a ação da Humanidade neste turno..."
        onChange={(e) => onChange(e.target.value)}
      />
      <div className="move-meta">
        <span className="char-count">
          {value.length} / 800
        </span>
        <button
          type="button"
          className="submit-btn"
          disabled={!canSubmit}
          onClick={onSubmit}
        >
          {resolving ? "Resolvendo…" : "Transmitir Jogada"}
        </button>
      </div>
    </section>
  );
}
