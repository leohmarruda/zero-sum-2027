import { useLocaleStore } from "../i18n";
import "./FooterNav.css";

interface Props {
  currentTurn: number;
  humanityWinTurn: number;
}

export function FooterNav({ currentTurn, humanityWinTurn }: Props) {
  const t = useLocaleStore((s) => s.t);
  const remaining = Math.max(humanityWinTurn - currentTurn, 0);
  return (
    <nav className="footer-nav footer-nav-solo">
      <span>
        <span className="turn-pips" aria-hidden="true">
          {Array.from({ length: Math.min(Math.max(humanityWinTurn, 0), 60) }, (_, i) => (
            <i key={i} className={i < currentTurn ? "on" : undefined} />
          ))}
        </span>
        {remaining > 0
          ? t("footer.turnsUntilEligible", { remaining })
          : t("footer.eligible")}
      </span>
    </nav>
  );
}
