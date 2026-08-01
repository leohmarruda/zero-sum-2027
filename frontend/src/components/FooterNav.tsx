import "./FooterNav.css";

interface Props {
  currentTurn: number;
  humanityWinTurn: number;
  onBackToSetup: () => void;
}

export function FooterNav({ currentTurn, humanityWinTurn, onBackToSetup }: Props) {
  const remaining = Math.max(humanityWinTurn - currentTurn, 0);
  return (
    <nav className="footer-nav">
      <button type="button" className="linkish" onClick={onBackToSetup}>
        ← Nova partida
      </button>
      <span>
        {remaining > 0
          ? `${remaining} turnos até elegibilidade de vitória humana`
          : "Humanidade elegível à vitória"}
      </span>
    </nav>
  );
}
