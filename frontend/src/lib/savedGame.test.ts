import { beforeEach, describe, expect, it } from "vitest";
import {
  clearSavedGame,
  loadDraft,
  loadGameId,
  saveDraft,
  saveGameId,
} from "./savedGame";

describe("savedGame", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("round-trips and clears the game id", () => {
    expect(loadGameId()).toBeNull();
    saveGameId("g1");
    expect(loadGameId()).toBe("g1");
    clearSavedGame();
    expect(loadGameId()).toBeNull();
  });

  it("only returns a draft for the same game and turn", () => {
    saveDraft("g1", 3, "move");
    expect(loadDraft("g1", 3)).toBe("move");
    expect(loadDraft("g1", 4)).toBe("");
    expect(loadDraft("g2", 3)).toBe("");
  });

  it("drops the draft when emptied or when the game is cleared", () => {
    saveDraft("g1", 1, "x");
    saveDraft("g1", 1, "");
    expect(loadDraft("g1", 1)).toBe("");
    saveDraft("g1", 1, "y");
    clearSavedGame();
    expect(loadDraft("g1", 1)).toBe("");
  });

  it("ignores corrupt draft storage", () => {
    localStorage.setItem("zero-sum-2027.move-draft", "{bad");
    expect(loadDraft("g1", 1)).toBe("");
  });
});
