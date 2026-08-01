import { GamePage } from "./pages/GamePage";
import { SetupPage } from "./pages/SetupPage";
import { useGameStore } from "./store/gameStore";

export default function App() {
  const screen = useGameStore((s) => s.screen);
  return screen === "setup" ? <SetupPage /> : <GamePage />;
}
