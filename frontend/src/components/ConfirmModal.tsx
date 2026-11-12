import { useEffect, useId } from "react";
import "./SetupForm.css";

interface Props {
  title: string;
  body: string;
  confirmLabel: string;
  cancelLabel: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmModal({
  title,
  body,
  confirmLabel,
  cancelLabel,
  onConfirm,
  onCancel,
}: Props) {
  const titleId = useId();

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onCancel();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onCancel]);

  return (
    <div className="modal-backdrop" role="presentation" onClick={onCancel}>
      <div
        className="modal"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby={titleId}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 id={titleId} className="modal-title">
          {title}
        </h2>
        <p className="modal-body">{body}</p>
        <div className="modal-actions">
          <span />
          <div className="modal-actions-end">
            <button
              type="button"
              className="modal-btn ghost"
              onClick={onCancel}
              autoFocus
            >
              {cancelLabel}
            </button>
            <button
              type="button"
              className="modal-btn danger"
              onClick={onConfirm}
            >
              {confirmLabel}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
