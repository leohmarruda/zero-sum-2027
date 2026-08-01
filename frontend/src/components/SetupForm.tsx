import type { SeatConfig } from "../api/client";
import "./SetupForm.css";

const ROLE_META: Record<
  SeatConfig["role"],
  { label: string; css: string }
> = {
  humanity: { label: "HUMANIDADE", css: "humanity" },
  rogue_ai: { label: "ROGUE AI", css: "rogue" },
  defender_ai: { label: "AI DEFENSORA", css: "defender" },
  dm: { label: "DM", css: "dm" },
};

interface Props {
  seats: SeatConfig[];
  submitting: boolean;
  onModelChange: (role: SeatConfig["role"], model: string) => void;
  onTempChange: (role: SeatConfig["role"], temperature: number) => void;
  onSubmit: () => void;
}

export function SetupForm({
  seats,
  submitting,
  onModelChange,
  onTempChange,
  onSubmit,
}: Props) {
  const ordered = ["humanity", "rogue_ai", "defender_ai", "dm"] as const;

  return (
    <>
      <section className="hero panel">
        <h1>Configurar assentos</h1>
        <p>
          MVP: você joga como Humanidade. Rogue AI, AI Defensora e DM são modelos
          configuráveis. 1 turno = 1 mês a partir de 2027-01.
        </p>
      </section>

      <section className="panel">
        <div className="panel-title">Assentos</div>
        {ordered.map((role) => {
          const seat = seats.find((s) => s.role === role)!;
          const meta = ROLE_META[role];
          const isHuman = seat.player_type === "human";
          return (
            <div className="seat" key={role}>
              <div className="seat-head">
                <div className="seat-role">
                  <span className={`dot ${meta.css}`} />
                  {meta.label}
                </div>
                <span className={`seat-type ${isHuman ? "human" : ""}`}>
                  {isHuman ? "HUMANO" : "IA"}
                </span>
              </div>
              {isHuman ? (
                <p className="note">
                  Assento fixo do jogador no MVP. Sem modelo LLM.
                </p>
              ) : (
                <div className="fields">
                  <label>
                    Modelo
                    <input
                      value={seat.model ?? ""}
                      onChange={(e) => onModelChange(role, e.target.value)}
                    />
                  </label>
                  <label>
                    Temp
                    <input
                      type="number"
                      min={0}
                      max={2}
                      step={0.1}
                      value={seat.temperature ?? 0.7}
                      onChange={(e) =>
                        onTempChange(role, Number.parseFloat(e.target.value) || 0)
                      }
                    />
                  </label>
                </div>
              )}
            </div>
          );
        })}
      </section>

      <div className="actions">
        <button
          type="button"
          className="submit-btn"
          disabled={submitting}
          onClick={onSubmit}
        >
          {submitting ? "Criando…" : "Iniciar Partida"}
        </button>
      </div>
    </>
  );
}
