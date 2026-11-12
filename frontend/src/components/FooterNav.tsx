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
        {remaining > 0
          ? t("footer.turnsUntilEligible", { remaining })
          : t("footer.eligible")}
      </span>
    </nav>
  );
}
