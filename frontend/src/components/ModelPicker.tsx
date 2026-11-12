import { useState } from "react";
import { useLocaleStore } from "../i18n";
import { MODEL_OPTIONS } from "../lib/models";

const CUSTOM = "__custom__";

interface Props {
  value: string;
  onChange: (model: string) => void;
}

/** Dropdown of suggested models, plus a free-text field for anything else. */
export function ModelPicker({ value, onChange }: Props) {
  const t = useLocaleStore((s) => s.t);
  const known = MODEL_OPTIONS.some((m) => m.id === value);
  const [custom, setCustom] = useState(!known && value !== "");
  const showCustom = custom || (!known && value !== "");

  return (
    <span className="model-picker">
      <select
        value={showCustom ? CUSTOM : value}
        onChange={(e) => {
          if (e.target.value === CUSTOM) {
            setCustom(true);
          } else {
            setCustom(false);
            onChange(e.target.value);
          }
        }}
      >
        {MODEL_OPTIONS.map((m) => (
          <option key={m.id} value={m.id}>
            {m.label}
          </option>
        ))}
        <option value={CUSTOM}>{t("setup.modelCustom")}</option>
      </select>
      {showCustom ? (
        <input
          value={value}
          spellCheck={false}
          placeholder="provider/model"
          onChange={(e) => onChange(e.target.value)}
        />
      ) : null}
    </span>
  );
}
