import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import { ZeroSumLedger } from "../components/ZeroSumLedger";
import { useLocaleStore } from "../i18n";

describe("ZeroSumLedger", () => {
  beforeEach(() => {
    useLocaleStore.getState().setLocale("en-US");
  });

  it("renders segment widths from score data", () => {
    render(
      <ZeroSumLedger
        title="Zero-Sum Ledger — Turn 03"
        scores={{
          hwg: { sm: 95, rc: 90, ic: 80, pc: 70, cs: 60 },
          selfish_ai: { sm: 3, rc: 5, ic: 10, pc: 20, cs: 25 },
          defender_ai: { sm: 2, rc: 5, ic: 10, pc: 10, cs: 15 },
        }}
      />,
    );

    expect(screen.getByText("Coercive Power")).toBeInTheDocument();
    expect(screen.getByText("Computing Power")).toBeInTheDocument();
    const hwgSm = screen.getByTestId("seg-sm-hwg");
    expect(hwgSm).toHaveStyle({ width: "95%" });
    expect(hwgSm).toHaveTextContent("95");

    const selfishSm = screen.getByTestId("seg-sm-selfish_ai");
    expect(selfishSm).toHaveStyle({ width: "3%" });
    expect(selfishSm).toHaveTextContent("");
  });

  it("shows per-turn deltas next to each seat's value", () => {
    render(
      <ZeroSumLedger
        title="Zero-Sum Ledger — Turn 04"
        scores={{
          hwg: { sm: 80, rc: 90, ic: 80, pc: 70, cs: 60 },
          selfish_ai: { sm: 20, rc: 10, ic: 20, pc: 30, cs: 40 },
        }}
        deltas={{
          hwg: { sm: -5, rc: 0.2, ic: 0, pc: 0, cs: 0 },
          selfish_ai: { sm: 5, rc: -0.2, ic: 0, pc: 0, cs: 0 },
        }}
      />,
    );

    expect(screen.getByTestId("agg-sm-hwg")).toHaveTextContent("HWG 80 −5");
    expect(screen.getByTestId("agg-sm-selfish_ai")).toHaveTextContent("SA 20 +5");
    // Changes that round to zero are not shown.
    expect(screen.getByTestId("agg-rc-hwg")).toHaveTextContent(/^HWG 90$/);
  });
});
