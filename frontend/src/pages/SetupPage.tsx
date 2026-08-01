import { SetupForm } from "../components/SetupForm";
import { StatusBar } from "../components/StatusBar";
import { useGameStore } from "../store/gameStore";

export function SetupPage() {
  const seats = useGameStore((s) => s.seats);
  const resolving = useGameStore((s) => s.resolving);
  const error = useGameStore((s) => s.error);
  const setSeatModel = useGameStore((s) => s.setSeatModel);
  const setSeatTemp = useGameStore((s) => s.setSeatTemp);
  const startGame = useGameStore((s) => s.startGame);

  return (
    <div className="app-shell">
      <StatusBar status="setup" />
      {error ? <div className="error-banner">{error}</div> : null}
      <SetupForm
        seats={seats}
        submitting={resolving}
        onModelChange={setSeatModel}
        onTempChange={setSeatTemp}
        onSubmit={() => void startGame()}
      />
    </div>
  );
}
