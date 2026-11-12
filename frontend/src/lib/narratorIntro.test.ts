import { describe, expect, it } from "vitest";
import { buildNarratorIntroFromLines } from "./narratorIntro";

const LINES = {
  open: "OPEN",
  hwg: "HWG",
  defender_ai: "DAI",
  paternalistic_ai: "PAI",
  misaligned: "MIS",
  het: "HET",
  gray_aliens: "GREY",
};

describe("buildNarratorIntroFromLines", () => {
  it("always includes the opening", () => {
    expect(buildNarratorIntroFromLines(["us", "china"], LINES)).toBe("OPEN");
  });

  it("includes role-dependent lines in order", () => {
    const text = buildNarratorIntroFromLines(
      [
        "hwg",
        "defender_ai",
        "paternalistic_ai",
        "selfish_ai",
        "het",
        "gray_aliens",
        "narrator",
      ],
      LINES,
    );
    expect(text).toBe("OPEN\n\nHWG\n\nDAI\n\nPAI\n\nMIS\n\nHET\n\nGREY");
  });

  it("emits misaligned once for any of PMAX/SAI/EAI", () => {
    expect(
      buildNarratorIntroFromLines(["paperclip_max", "exterminator_ai"], LINES),
    ).toBe("OPEN\n\nMIS");
  });
});
