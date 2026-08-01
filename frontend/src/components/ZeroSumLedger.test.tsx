import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ZeroSumLedger } from "../components/ZeroSumLedger";

describe("ZeroSumLedger", () => {
  it("renders segment widths from score data", () => {
    render(
      <ZeroSumLedger
        title="Ledger Zero-Sum — Turno 03"
        scores={{
          humanity: { sm: 95, rc: 90, ic: 80, pc: 70, cs: 60 },
          rogue_ai: { sm: 3, rc: 5, ic: 10, pc: 20, cs: 25 },
          defender_ai: { sm: 2, rc: 5, ic: 10, pc: 10, cs: 15 },
        }}
      />,
    );

    expect(screen.getByText("Soberania Militar")).toBeInTheDocument();
    const humanitySm = screen.getByTestId("seg-sm-humanity");
    expect(humanitySm).toHaveStyle({ width: "95%" });
    expect(humanitySm).toHaveTextContent("95");

    const rogueSm = screen.getByTestId("seg-sm-rogue_ai");
    expect(rogueSm).toHaveStyle({ width: "3%" });
    // Labels omitted under ~5%
    expect(rogueSm).toHaveTextContent("");
  });
});
