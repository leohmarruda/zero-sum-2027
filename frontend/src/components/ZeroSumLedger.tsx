import type { CategoryScores, ScoreDeltas } from "../api/client";
import { ROLE_CSS, ROLE_SHORT, type PlayableRole } from "../api/client";
import { roleMessageKey, useLocaleStore, type MessageKey } from "../i18n";
import "./ZeroSumLedger.css";

const CATEGORY_KEYS: {
  key: keyof CategoryScores;
  labelKey: MessageKey;
  descKey: MessageKey;
}[] = [
  { key: "pc", labelKey: "category.pc", descKey: "categoryDesc.pc" },
  { key: "rc", labelKey: "category.rc", descKey: "categoryDesc.rc" },
  { key: "cs", labelKey: "category.cs", descKey: "categoryDesc.cs" },
  { key: "ic", labelKey: "category.ic", descKey: "categoryDesc.ic" },
  { key: "sm", labelKey: "category.sm", descKey: "categoryDesc.sm" },
];

/** "+3" / "−4" for a visible per-turn change; null when it rounds to zero. */
function formatDelta(d: number | undefined): { text: string; up: boolean } | null {
  if (d === undefined) return null;
  const r = Math.round(d);
  if (r === 0) return null;
  return r > 0 ? { text: ` +${r}`, up: true } : { text: ` −${Math.abs(r)}`, up: false };
}

interface Props {
  title: string;
  scores: Record<string, CategoryScores>;
  /** Change versus the previous turn, by seat role then category. */
  deltas?: ScoreDeltas | null;
  displayNames?: Record<string, string | null | undefined>;
  /** Seat role played by the human, flagged with a YOU badge in the legend. */
  humanRole?: string;
}

export function ZeroSumLedger({
  title,
  scores,
  deltas,
  displayNames,
  humanRole,
}: Props) {
  const t = useLocaleStore((s) => s.t);
  const roles = Object.keys(scores);

  const labelFor = (role: string) => {
    const custom = displayNames?.[role];
    if (custom) return custom;
    return t(roleMessageKey(role));
  };

  const shortFor = (role: string) =>
    ROLE_SHORT[role as PlayableRole] ?? role.slice(0, 2).toUpperCase();

  return (
    <section className="panel">
      <div className="panel-title">
        <span>{title}</span>
      </div>

      <div className="legend">
        {roles.map((role) => (
          <div className="legend-item" key={role}>
            <span className={`swatch ${ROLE_CSS[role as PlayableRole] ?? "hwg"}`} />
            {labelFor(role)}
            {role === humanRole ? <span className="you-badge">{t("setup.playerHuman")}</span> : null}
          </div>
        ))}
      </div>

      {CATEGORY_KEYS.map(({ key, labelKey, descKey }) => {
        const label = t(labelKey);
        const description = t(descKey);
        const values = roles.map((role) => ({
          role,
          css: ROLE_CSS[role as PlayableRole] ?? "hwg",
          short: shortFor(role),
          value: scores[role][key],
        }));
        const withDelta = values.map((v) => ({
          ...v,
          delta: formatDelta(deltas?.[v.role]?.[key]),
        }));
        const agg = withDelta
          .map((v) => `${v.short} ${Math.round(v.value)}${v.delta?.text ?? ""}`)
          .join(" · ");
        return (
          <div className="ledger-row" key={key} data-testid={`ledger-${key}`}>
            <div className="ledger-label">
              <span title={description}>{label}</span>
              <span className="agg">
                {withDelta.map((v, i) => (
                  <span key={v.role} data-testid={`agg-${key}-${v.role}`}>
                    {i > 0 ? " · " : ""}
                    {v.short}{" "}
                    <b className={`agg-val ${v.css}`}>{Math.round(v.value)}</b>
                    {v.delta ? (
                      <span className={`delta ${v.delta.up ? "up" : "down"}`}>
                        {v.delta.text}
                      </span>
                    ) : null}
                  </span>
                ))}
              </span>
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
