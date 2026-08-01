# Cost estimate — full game dry_run (Gate A assumption #4)

**Date:** 2026-08-01  
**Script:** `backend/scripts/estimate_game_cost.py`  
**Method:** `llmcall` `dry_run=True` for input tokens; USD from litellm
`openai/gpt-4o-mini` rates; assumed outputs 350 (seat) / 900 (DM) tokens.

| Field | Value |
|---|---|
| Runtime model | `openrouter/openai/gpt-4o-mini` |
| Pricing model | `openai/gpt-4o-mini` ($0.00015 / $0.0006 per 1k in/out) |
| Turns | 60 |
| Calls / turn | 3 (rogue + defender + DM; humanity is human) |
| Total calls | 180 |
| Cost / turn | **~$0.00113** |
| Full game (60 turns) | **~$0.068** |
| Input-only / turn | ~$0.00017 |

**Verdict:** acceptable for Lite prototype iteration. Even 10 full test
games ≈ $0.68 at these rates.

**Caveats:** OpenRouter list prices may differ slightly from OpenAI map
rates; real completion lengths vary; early wins (<60 turns) cost less.
