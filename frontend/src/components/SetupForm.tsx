import { useEffect, useId, useRef, useState } from "react";
import {
  DEFAULT_PLAYABLE_ROLES,
  PLAYABLE_ROLES,
  ROLE_CSS,
  type PlayableRole,
  type SeatConfig,
  type SeatRole,
} from "../api/client";
import {
  roleDescKey,
  roleHasDelayedWin,
  roleMessageKey,
  roleStartingKey,
  useLocaleStore,
} from "../i18n";
import {
  estimateGameCost,
  formatUsdEstimate,
} from "../lib/costEstimate";
import "./SetupForm.css";

const DEFAULT_MODEL = "openrouter/openai/gpt-4o-mini";

interface Props {
  seats: SeatConfig[];
  submitting: boolean;
  error?: string | null;
  setupIntro: string;
  onChangeSeats: (seats: SeatConfig[]) => void;
  onSubmit: () => void;
}

function playableSeats(seats: SeatConfig[]) {
  return seats.filter((s) => s.role !== "narrator");
}

function narratorSeat(seats: SeatConfig[]) {
  return seats.find((s) => s.role === "narrator")!;
}

function CustomNameModal({
  roleLabel,
  initialName,
  onSave,
  onClose,
}: {
  roleLabel: string;
  initialName: string;
  onSave: (name: string | null) => void;
  onClose: () => void;
}) {
  const t = useLocaleStore((s) => s.t);
  const titleId = useId();
  const inputRef = useRef<HTMLInputElement>(null);
  const [draft, setDraft] = useState(initialName);

  useEffect(() => {
    inputRef.current?.focus();
    inputRef.current?.select();
  }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const commit = (value: string) => {
    const trimmed = value.trim().slice(0, 64);
    onSave(trimmed || null);
  };

  return (
    <div
      className="modal-backdrop"
      role="presentation"
      onClick={onClose}
    >
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 id={titleId} className="modal-title">
          {t("setup.customName")}
        </h2>
        <p className="modal-role">{roleLabel}</p>
        <label className="modal-field">
          <span className="sr-only">{t("setup.customName")}</span>
          <input
            ref={inputRef}
            value={draft}
            maxLength={64}
            placeholder={t("setup.customNamePlaceholder")}
            onChange={(e) => setDraft(e.target.value.slice(0, 64))}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                commit(draft);
              }
            }}
          />
        </label>
        <div className="modal-actions">
          {draft.trim() ? (
            <button
              type="button"
              className="linkish danger"
              onClick={() => {
                setDraft("");
                onSave(null);
              }}
            >
              {t("setup.customNameClear")}
            </button>
          ) : (
            <span />
          )}
          <div className="modal-actions-end">
            <button type="button" className="modal-btn ghost" onClick={onClose}>
              {t("setup.customNameCancel")}
            </button>
            <button
              type="button"
              className="modal-btn primary"
              onClick={() => commit(draft)}
            >
              {t("setup.customNameSave")}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export function SetupForm({
  seats,
  submitting,
  error = null,
  setupIntro,
  onChangeSeats,
  onSubmit,
}: Props) {
  const t = useLocaleStore((s) => s.t);
  const playable = playableSeats(seats);
  const narrator = narratorSeat(seats);
  const used = new Set(seats.map((s) => s.role));
  const available = PLAYABLE_ROLES.filter((r) => !used.has(r));
  const hasHwg = used.has("hwg");
  const cost = estimateGameCost(seats);
  const [namingRole, setNamingRole] = useState<SeatRole | null>(null);

  const roleBlurb = (role: SeatRole) => {
    const parts = [t(roleDescKey(role)), t(roleStartingKey(role, hasHwg))];
    if (roleHasDelayedWin(role)) parts.push(t("roleStart.delayedWin"));
    return parts.join(" ");
  };

  const roleLabel = (role: SeatRole) => t(roleMessageKey(role));

  const seatLabel = (seat: SeatConfig) => {
    const role = roleLabel(seat.role);
    const name = seat.display_name?.trim();
    return name ? t("setup.namedRole", { name, role }) : role;
  };

  const updateSeat = (role: SeatRole, patch: Partial<SeatConfig>) => {
    onChangeSeats(seats.map((s) => (s.role === role ? { ...s, ...patch } : s)));
  };

  const setHuman = (role: PlayableRole) => {
    onChangeSeats(
      seats.map((s) => {
        if (s.role === "narrator") return s;
        if (s.role === role) {
          return { ...s, player_type: "human", model: null, temperature: null };
        }
        return {
          ...s,
          player_type: "ai",
          model: s.model ?? DEFAULT_MODEL,
          temperature: s.temperature ?? 0.7,
        };
      }),
    );
  };

  const changeRole = (from: PlayableRole, to: PlayableRole) => {
    if (from === to) return;
    if (used.has(to)) return;
    onChangeSeats(
      seats.map((s) => (s.role === from ? { ...s, role: to } : s)),
    );
  };

  const addRole = (role: PlayableRole) => {
    onChangeSeats([
      ...playable,
      {
        role,
        player_type: "ai",
        model: DEFAULT_MODEL,
        temperature: 0.7,
        display_name: null,
      },
      narrator,
    ]);
  };

  const removeRole = (role: PlayableRole) => {
    if (playable.length <= 2) return;
    const remaining = playable.filter((s) => s.role !== role);
    const hadHuman = playable.find((s) => s.role === role)?.player_type === "human";
    const next = remaining.map((s, i) =>
      hadHuman && i === 0
        ? { ...s, player_type: "human" as const, model: null, temperature: null }
        : s,
    );
    onChangeSeats([...next, narrator]);
  };

  const namingSeat =
    namingRole == null ? null : seats.find((s) => s.role === namingRole) ?? null;

  return (
    <>
      <section className="panel intro">
        <p>{setupIntro}</p>
      </section>

      <section className="hero panel">
        <h1>{t("setup.title")}</h1>
        <p>{t("setup.blurb")}</p>
      </section>

      <section className="panel">
        <div className="panel-title">{t("setup.seats")}</div>
        {playable.map((seat) => {
          const role = seat.role as PlayableRole;
          const isHuman = seat.player_type === "human";
          const roleOptions = [
            role,
            ...PLAYABLE_ROLES.filter((r) => !used.has(r)),
          ];
          return (
            <div className="seat" key={role}>
              <div className="seat-head">
                <div className="seat-role">
                  <span className={`dot ${ROLE_CSS[role]}`} />
                  <select
                    className="role-select"
                    value={role}
                    onChange={(e) =>
                      changeRole(role, e.target.value as PlayableRole)
                    }
                  >
                    {roleOptions.map((r) => (
                      <option key={r} value={r}>
                        {r === role ? seatLabel(seat) : roleLabel(r)}
                      </option>
                    ))}
                  </select>
                  <button
                    type="button"
                    className={`name-btn${seat.display_name ? " set" : ""}`}
                    onClick={() => setNamingRole(role)}
                  >
                    {t("setup.customName")}
                  </button>
                </div>
                <div className="seat-head-actions">
                  {isHuman ? (
                    <span className="seat-type human">{t("setup.playerHuman")}</span>
                  ) : (
                    <button
                      type="button"
                      className="seat-type take-seat"
                      onClick={() => setHuman(role)}
                    >
                      {t("setup.takeSeat")}
                    </button>
                  )}
                  {playable.length > 2 ? (
                    <button
                      type="button"
                      className="linkish danger"
                      onClick={() => removeRole(role)}
                    >
                      {t("setup.remove")}
                    </button>
                  ) : null}
                </div>
              </div>

              <p className="seat-desc">{roleBlurb(role)}</p>

              {!isHuman ? (
                <div className="fields">
                  <label>
                    {t("setup.model")}
                    <input
                      value={seat.model ?? ""}
                      onChange={(e) => updateSeat(role, { model: e.target.value })}
                    />
                  </label>
                  <label>
                    {t("setup.temp")}
                    <input
                      type="number"
                      min={0}
                      max={2}
                      step={0.1}
                      value={seat.temperature ?? 0.7}
                      onChange={(e) =>
                        updateSeat(role, {
                          temperature: Number.parseFloat(e.target.value) || 0,
                        })
                      }
                    />
                  </label>
                </div>
              ) : null}
            </div>
          );
        })}

        <div className="add-row">
          {available.length ? (
            <label className="add-role">
              {t("setup.addRole")}
              <select
                defaultValue=""
                onChange={(e) => {
                  const value = e.target.value as PlayableRole;
                  if (value) addRole(value);
                  e.target.value = "";
                }}
              >
                <option value="" disabled>
                  —
                </option>
                {available.map((r) => (
                  <option key={r} value={r}>
                    {t(roleMessageKey(r))}
                  </option>
                ))}
              </select>
            </label>
          ) : (
            <p className="note">{t("setup.noMoreRoles")}</p>
          )}
        </div>
      </section>

      {error ? <div className="error-banner">{error}</div> : null}

      <section className="panel">
        <div className="seat">
          <div className="seat-head">
            <div className="seat-role">
              <span className={`dot ${ROLE_CSS.narrator}`} />
              <span className="role-static">{roleLabel("narrator")}</span>
            </div>
            <span className="seat-type">{t("setup.fixedRole")}</span>
          </div>
          <p className="seat-desc">{roleBlurb("narrator")}</p>
          <div className="fields">
            <label>
              {t("setup.model")}
              <input
                value={narrator.model ?? ""}
                onChange={(e) =>
                  updateSeat("narrator", { model: e.target.value })
                }
              />
            </label>
            <label>
              {t("setup.temp")}
              <input
                type="number"
                min={0}
                max={2}
                step={0.1}
                value={narrator.temperature ?? 0.4}
                onChange={(e) =>
                  updateSeat("narrator", {
                    temperature: Number.parseFloat(e.target.value) || 0,
                  })
                }
              />
            </label>
          </div>
        </div>
      </section>

      <div className="actions">
        <div
          className="cost-estimate"
          title={t("setup.estCostHint")}
        >
          <span className="cost-estimate-label">{t("setup.estCost")}</span>
          <span className="cost-estimate-value">
            {t("setup.estCostValue", {
              cost: formatUsdEstimate(cost.estimatedCostUsd),
              turns: cost.turns,
            })}
          </span>
        </div>
        <button
          type="button"
          className="submit-btn"
          disabled={submitting}
          onClick={onSubmit}
        >
          {submitting ? t("setup.creating") : t("setup.start")}
        </button>
      </div>

      {namingSeat ? (
        <CustomNameModal
          roleLabel={roleLabel(namingSeat.role)}
          initialName={namingSeat.display_name ?? ""}
          onClose={() => setNamingRole(null)}
          onSave={(name) => {
            updateSeat(namingSeat.role, { display_name: name });
            setNamingRole(null);
          }}
        />
      ) : null}
    </>
  );
}

export function buildDefaultSeats(): SeatConfig[] {
  return [
    ...DEFAULT_PLAYABLE_ROLES.map((role, i) =>
      i === 0
        ? {
            role,
            player_type: "human" as const,
            model: null,
            temperature: null,
            display_name: null,
          }
        : {
            role,
            player_type: "ai" as const,
            model: DEFAULT_MODEL,
            temperature: 0.7,
            display_name: null,
          },
    ),
    {
      role: "narrator",
      player_type: "ai",
      model: DEFAULT_MODEL,
      temperature: 0.4,
      display_name: null,
    },
  ];
}
