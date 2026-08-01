import type { CategoryScores, ScoredRole } from "../api/client";
import "./ZeroSumLedger.css";

const CATEGORIES: { key: keyof CategoryScores; label: string }[] = [
  { key: "sm", label: "Soberania Militar" },
  { key: "rc", label: "Recursos Críticos" },
  { key: "ic", label: "Infraestrutura Crítica" },
  { key: "pc", label: "Poder Computacional" },
  { key: "cs", label: "Automação de Suprimentos" },
];

const ORDER: { role: ScoredRole; css: string; short: string }[] = [
  { role: "humanity", css: "humanity", short: "H" },
  { role: "rogue_ai", css: "rogue", short: "R" },
  { role: "defender_ai", css: "defender", short: "D" },
];

interface Props {
  title: string;
  scores: Record<ScoredRole, CategoryScores>;
}

export function ZeroSumLedger({ title, scores }: Props) {
  return (
    <section className="panel">
      <div className="panel-title">
        <span>{title}</span>
        <div className="legend">
          <div className="legend-item">
            <span className="swatch humanity" />
            Humanidade
          </div>
          <div className="legend-item">
            <span className="swatch rogue" />
            Rogue AI
          </div>
          <div className="legend-item">
            <span className="swatch defender" />
            AI Defensora
          </div>
        </div>
      </div>

      {CATEGORIES.map(({ key, label }) => {
        const values = ORDER.map(({ role, css, short }) => ({
          role,
          css,
          short,
          value: scores[role][key],
        }));
        const agg = values
          .map((v) => `${v.short} ${Math.round(v.value)}`)
          .join(" · ");
        return (
          <div className="ledger-row" key={key} data-testid={`ledger-${key}`}>
            <div className="ledger-label">
              <span>{label}</span>
              <span className="agg">{agg}</span>
            </div>
            <div className="ledger-track" role="img" aria-label={`${label}: ${agg}`}>
              {values.map((v) =>
                v.value <= 0 ? null : (
                  <div
                    key={v.role}
                    className={`seg ${v.css}`}
                    style={{ width: `${v.value}%` }}
                    data-testid={`seg-${key}-${v.role}`}
                  >
                    {v.value >= 5 ? Math.round(v.value) : null}
                  </div>
                ),
              )}
            </div>
          </div>
        );
      })}
    </section>
  );
}
