import { useEffect, useState } from "react";
import { getContent } from "../api/client";
import { SetupForm } from "../components/SetupForm";
import { SiteFooter } from "../components/SiteFooter";
import { StatusBar } from "../components/StatusBar";
import { useLocaleStore } from "../i18n";
import { useGameStore } from "../store/gameStore";

const SETUP_INTRO_FALLBACK =
  "A text RPG game about AGI competition and humanity survival after 2027.";

export function SetupPage() {
  const seats = useGameStore((s) => s.seats);
  const resolving = useGameStore((s) => s.resolving);
  const error = useGameStore((s) => s.error);
  const setSeats = useGameStore((s) => s.setSeats);
  const startGame = useGameStore((s) => s.startGame);
  const locale = useLocaleStore((s) => s.locale);
  const [setupIntro, setSetupIntro] = useState(SETUP_INTRO_FALLBACK);

  useEffect(() => {
    let cancelled = false;
    void getContent(locale)
      .then((bundle) => {
        if (!cancelled) setSetupIntro(bundle.setup_intro);
      })
      .catch(() => {
        /* keep fallback */
      });
    return () => {
      cancelled = true;
    };
  }, [locale]);

  return (
    <div className="app-shell">
      <StatusBar status="setup" />
      <SetupForm
        seats={seats}
        submitting={resolving}
        error={error}
        setupIntro={setupIntro}
        onChangeSeats={setSeats}
        onSubmit={() => void startGame()}
      />
      <SiteFooter />
    </div>
  );
}
