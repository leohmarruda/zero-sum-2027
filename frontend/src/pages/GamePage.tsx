import { FooterNav } from "../components/FooterNav";
import { MovePanel } from "../components/MovePanel";
import { StatusBar } from "../components/StatusBar";
import { TransmissionPanel } from "../components/TransmissionPanel";
import { ZeroSumLedger } from "../components/ZeroSumLedger";
import { useGameStore } from "../store/gameStore";
import "../components/FooterNav.css";

const MONTHS = [
  "JAN",
  "FEV",
  "MAR",
  "ABR",
  "MAI",
  "JUN",
  "JUL",
  "AGO",
  "SET",
  "OUT",
  "NOV",
  "DEZ",
];

function narrativeDate(turn: number): string {
  const year = 2027 + Math.floor((turn - 1) / 12);
  const month = ((turn - 1) % 12) + 1;
  return `${year}-${String(month).padStart(2, "0")}-01`;
}

function turnMeta(turn: number): string {
  const year = 2027 + Math.floor((turn - 1) / 12);
  const month = MONTHS[(turn - 1) % 12];
  return `TURNO ${String(turn).padStart(2, "0")} · ${month} ${year}`;
}

export function GamePage() {
  const game = useGameStore((s) => s.game)!;
  const lastAdjudication = useGameStore((s) => s.lastAdjudication);
  const moveDraft = useGameStore((s) => s.moveDraft);
  const resolving = useGameStore((s) => s.resolving);
  const error = useGameStore((s) => s.error);
  const setMoveDraft = useGameStore((s) => s.setMoveDraft);
  const submitAndResolve = useGameStore((s) => s.submitAndResolve);
  const backToSetup = useGameStore((s) => s.backToSetup);

  const ended = game.status === "ended";
  const scores = game.current_scores;
  const ledgerTurn = ended
    ? game.current_turn
    : Math.max(game.current_turn - 1, 0);

  return (
    <div className="app-shell">
      <StatusBar
        status={game.status}
        winner={game.winner}
        turnLabel={
          ended
            ? `FIM · TURNO ${game.current_turn}`
            : turnMeta(game.current_turn)
        }
      />
      {error ? <div className="error-banner">{error}</div> : null}

      {scores ? (
        <ZeroSumLedger
          title={`Ledger Zero-Sum — Turno ${String(ledgerTurn).padStart(2, "0")}`}
          scores={scores}
        />
      ) : null}

      {lastAdjudication ? (
        <TransmissionPanel
          turnNumber={lastAdjudication.turn_number}
          dateLabel={narrativeDate(lastAdjudication.turn_number)}
          narrative={lastAdjudication.world_narrative}
          feedback={lastAdjudication.seat_feedback.humanity}
        />
      ) : (
        <section className="panel transmission-empty">
          <div className="panel-title">
            <span>Aguardando primeira transmissão</span>
          </div>
          <p style={{ color: "var(--text-muted)", fontSize: 14, lineHeight: 1.55 }}>
            Envie a jogada do turno {game.current_turn} para o DM arbitrar o mês.
          </p>
        </section>
      )}

      {!ended ? (
        <MovePanel
          title={`Sua Jogada — Turno ${String(game.current_turn).padStart(2, "0")} (${MONTHS[(game.current_turn - 1) % 12]} ${2027 + Math.floor((game.current_turn - 1) / 12)})`}
          value={moveDraft}
          resolving={resolving}
          onChange={setMoveDraft}
          onSubmit={() => void submitAndResolve()}
        />
      ) : (
        <section className="panel">
          <div className="panel-title">
            <span>Partida encerrada</span>
          </div>
          <p style={{ color: "var(--text-muted)", fontSize: 14 }}>
            {game.winner
              ? `Vencedor: ${game.winner}`
              : "Empate — teto de turnos atingido."}
          </p>
        </section>
      )}

      {!ended ? (
        <FooterNav
          currentTurn={game.current_turn}
          humanityWinTurn={game.humanity_win_turn}
          onBackToSetup={backToSetup}
        />
      ) : (
        <nav className="footer-nav">
          <button type="button" className="linkish" onClick={backToSetup}>
            ← Nova partida
          </button>
        </nav>
      )}
    </div>
  );
}
