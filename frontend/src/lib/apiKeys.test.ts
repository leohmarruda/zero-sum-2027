import { beforeEach, describe, expect, it } from "vitest";
import { apiKeyHeaders, loadApiKeys, saveApiKeys } from "./apiKeys";

describe("apiKeys", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("round-trips keys and drops blanks", () => {
    expect(saveApiKeys({ openrouter: "  sk-or  ", openai: "   " })).toBe(true);
    expect(loadApiKeys()).toEqual({ openrouter: "sk-or" });
  });

  it("builds one header per stored provider", () => {
    saveApiKeys({ openrouter: "a", anthropic: "b" });
    expect(apiKeyHeaders()).toEqual({
      "X-Api-Key-openrouter": "a",
      "X-Api-Key-anthropic": "b",
    });
  });

  it("removes storage when every key is cleared", () => {
    saveApiKeys({ openai: "x" });
    saveApiKeys({});
    expect(loadApiKeys()).toEqual({});
    expect(apiKeyHeaders()).toEqual({});
  });

  it("ignores corrupt storage", () => {
    localStorage.setItem("zero-sum-2027.api-keys", "{not json");
    expect(loadApiKeys()).toEqual({});
  });
});
