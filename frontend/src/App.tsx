import { useEffect } from "react";
import { SiteFooter } from "./components/SiteFooter";
import { StatusBar } from "./components/StatusBar";
import { GamePage } from "./pages/GamePage";
import { SetupPage } from "./pages/SetupPage";
import { useGameStore } from "./store/gameStore";

export default function App() {
  const screen = useGameStore((s) => s.screen);
  const restoring = useGameStore((s) => s.restoring);
  const restoreGame = useGameStore((s) => s.restoreGame);

  useEffect(() => {
    void restoreGame();
  }, [restoreGame]);

  if (restoring) {
    return (
      <div className="app-shell" aria-busy="true">
        <StatusBar status="in_progress" />
        <SiteFooter />
      </div>
    );
  }
  return screen === "setup" ? <SetupPage /> : <GamePage />;
}
