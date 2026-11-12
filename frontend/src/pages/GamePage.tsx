import { FooterNav } from "../components/FooterNav";
import { MovePanel } from "../components/MovePanel";
import { StatusBar } from "../components/StatusBar";
import { TransmissionPanel } from "../components/TransmissionPanel";
import { ZeroSumLedger } from "../components/ZeroSumLedger";
import { isOffDraft } from "../api/client";
import {
  monthLabel,
  roleMessageKey,
  useLocaleStore,
  type MessageKey,
} from "../i18n";
import { useGameStore } from "../store/gameStore";
import "../components/FooterNav.css";

const ENDING_KEYS: readonly string[] = [
  "hegemony",
  "containment",
  "uneasy_hegemony",
  "bipolar_standoff",
  "multipolar_balance",
];

function narrativeDate(turn: number): string {
  const year = 2027 + Math.floor((turn - 1) / 12);
  const month = ((turn - 1) % 12) + 1;
  return `${year}-${String(month).padStart(2, "0")}-01`;
}

function turnCalendar(turn: number) {
  const safe = Math.max(turn, 1);
  const monthIndex = (safe - 1) % 12;
  const year = 2027 + Math.floor((safe - 1) / 12);
  return { monthIndex, year };
}

export function GamePage() {
  const t = useLocaleStore((s) => s.t);
  const locale = useLocaleStore((s) => s.locale);
  const game = useGameStore((s) => s.game)!;
  const viewedTurn = useGameStore((s) => s.viewedTurn);
  const viewedScores = useGameStore((s) => s.viewedScores);
  const viewedDeltas = useGameStore((s) => s.viewedDeltas);
  const lastAdjudication = useGameStore((s) => s.lastAdjudication);
  const lastOffReply = useGameStore((s) => s.lastOffReply);
  const lastRejection = useGameStore((s) => s.lastRejection);
  const moveDraft = useGameStore((s) => s.moveDraft);
  const resolving = useGameStore((s) => s.resolving);
  const error = useGameStore((s) => s.error);
  const setMoveDraft = useGameStore((s) => s.setMoveDraft);
  const submitAndResolve = useGameStore((s) => s.submitAndResolve);
  const viewTurn = useGameStore((s) => s.viewTurn);
  const backToSetup = useGameStore((s) => s.backToSetup);

  const ended = game.status === "ended";
  const scores = viewedScores ?? game.current_scores;
  const maxTurn = Math.max(game.current_turn, 1);
  const isCurrentView =
    viewedTurn === game.current_turn && game.status !== "ended";
  const isReplayView = !isCurrentView;

  const humanSeat =
    game.seats.find((s) => s.player_type === "human" && s.role !== "narrator") ??
    null;
  const humanRole = humanSeat?.role ?? "hwg";
  const humanLabel =
    humanSeat?.display_name || t(roleMessageKey(humanRole));

  const displayNames = Object.fromEntries(
    game.seats.map((s) => [s.role, s.display_name]),
  );

  const ledgerCal = turnCalendar(viewedTurn);
  const ledgerMonthRaw = monthLabel(locale, ledgerCal.monthIndex);
  const ledgerMonth =
    ledgerMonthRaw.charAt(0) + ledgerMonthRaw.slice(1).toLowerCase();

  // "Next turn" move label is the month after the turn you're about to play.
  // Replay labels use that past turn's own month.
  const moveCal = turnCalendar(isReplayView ? viewedTurn : viewedTurn + 1);
  const moveMonthRaw = monthLabel(locale, moveCal.monthIndex);
  const moveMonth =
    moveMonthRaw.charAt(0) + moveMonthRaw.slice(1).toLowerCase();

  const winnerLabel = game.winner
    ? displayNames[game.winner] || t(roleMessageKey(game.winner))
    : null;

  const endingLabel =
    game.ending && ENDING_KEYS.includes(game.ending)
      ? t(`ending.${game.ending}` as MessageKey)
      : null;

  const offMode = isOffDraft(moveDraft);
  const showIntro = viewedTurn === 1;

  return (
    <div className="app-shell">
      <StatusBar
        status={game.status}
        winner={winnerLabel}
        onSettings={backToSetup}
      />
      {error ? <div className="error-banner">{error}</div> : null}

      {scores ? (
        <ZeroSumLedger
          title={t("ledger.title", {
            turn: viewedTurn,
            month: ledgerMonth,
            year: ledgerCal.year,
          })}
          scores={scores}
          deltas={viewedDeltas}
          displayNames={displayNames}
          canGoPrev={viewedTurn > 1}
          canGoNext={viewedTurn < maxTurn}
          onPrev={() => void viewTurn(viewedTurn - 1)}
          onNext={() => void viewTurn(viewedTurn + 1)}
        />
      ) : null}

      {showIntro ? (
        <TransmissionPanel
          headLabel={t("transmission.introHead")}
          dateLabel={narrativeDate(1)}
          narrative={
            game.narrator_intro ??
            t("transmission.awaitingBody", { turn: game.current_turn })
          }
        />
      ) : lastAdjudication ? (
        <TransmissionPanel
          turnNumber={viewedTurn}
          dateLabel={narrativeDate(viewedTurn)}
          narrative={lastAdjudication.world_narrative}
          feedback={lastAdjudication.seat_feedback[humanRole]}
          feedbackSeatLabel={humanLabel}
        />
      ) : null}

      {lastRejection ? (
        <TransmissionPanel
          headLabel={t("transmission.rejectHead")}
          dateLabel={narrativeDate(game.current_turn)}
          narrative={lastRejection}
        />
      ) : null}

      {lastOffReply ? (
        <TransmissionPanel
          headLabel={t("transmission.offHead")}
          dateLabel={narrativeDate(lastOffReply.turn_number)}
          question={lastOffReply.question}
          narrative={lastOffReply.answer}
        />
      ) : null}

      {!ended || isReplayView ? (
        <MovePanel
          title={
            isReplayView
              ? t("move.titleReplay", {
                  turn: viewedTurn,
                  month: moveMonth,
                  year: moveCal.year,
                })
              : t("move.title", {
                  month: moveMonth,
                  year: moveCal.year,
                })
          }
          value={moveDraft}
          resolving={resolving}
          offMode={offMode && !isReplayView}
          replayMode={isReplayView}
          onChange={setMoveDraft}
          onSubmit={() => void submitAndResolve()}
        />
      ) : (
        <section className="panel">
          <div className="panel-title">
            <span>{t("game.endedTitle")}</span>
          </div>
          <p style={{ color: "var(--text-muted)", fontSize: 14 }}>
            {winnerLabel
              ? t("game.winner", { winner: winnerLabel })
              : t("game.drawCap")}
          </p>
        </section>
      )}

      {ended && viewedTurn === game.current_turn ? (
        <>
          <section className="panel" data-testid="game-ending">
            <div className="panel-title">
              <span>{t("game.endedTitle")}</span>
            </div>
            <p style={{ color: "var(--text-muted)", fontSize: 14 }}>
              {winnerLabel
                ? t("game.winner", { winner: winnerLabel })
                : t("game.drawCap")}
              {endingLabel
                ? ` · ${t("game.ending", { ending: endingLabel })}`
                : ""}
            </p>
          </section>
          {game.epilogue ? (
            <TransmissionPanel
              headLabel={t("game.epilogueTitle")}
              dateLabel={narrativeDate(game.current_turn)}
              narrative={game.epilogue}
            />
          ) : null}
        </>
      ) : null}

      {!ended ? (
        <FooterNav
          currentTurn={game.current_turn}
          humanityWinTurn={game.humanity_win_turn}
        />
      ) : null}
    </div>
  );
}
