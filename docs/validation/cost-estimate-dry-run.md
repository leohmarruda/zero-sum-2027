# Cost estimate — full game dry_run (Gate A assumption #4)

**Date:** 2026-08-01 (default lineup; still the reference estimate)  
**Updated:** 2026-08-02 — context-scaling compare (`--compare`, turn 55)  
**Script:** `backend/scripts/estimate_game_cost.py`  
**Method:** `llmcall` `dry_run=True` for input tokens; USD from litellm
`openai/gpt-4o-mini` rates; assumed outputs 350 (seat) / 900 (Narrator)
tokens.

## Baseline (production = rolling digest)

Production Narrator prompts carry a **rolling `world_state_digest`**
(~200–400 tokens, rewritten each adjudication) plus this turn's scores/moves.
No raw match-history dump — input stays **O(1) per turn**, full-game **O(T)**.

| Field | Value |
|---|---|
| Runtime model | `openrouter/openai/gpt-4o-mini` |
| Pricing model | `openai/gpt-4o-mini` ($0.00015 / $0.0006 per 1k in/out) |
| Turns | 60 |
| Lineup modeled | Default: 2 AI seats + Narrator (human occupies the 3rd playable) |
| Calls / turn | 3 (2 seat moves + Narrator adjudication) |
| Total calls | 180 |
| Cost / turn | **~$0.00127** (re-measured 2026-08-02; digest ≈ +150 input tok) |
| Full game (60 turns) | **~$0.076–0.077** |
| Input-only / turn | ~$0.00031 |

**Verdict:** acceptable for Lite prototype iteration on the **default
lineup**. Even 10 full test games ≈ $0.76 at these rates.

## Context scaling (why turn-1 dry_run alone is not enough)

If continuity used **raw prior `world_narrative`s** instead of a digest,
DM input tokens grow **O(turn)** and full-game cost **~O(T²)**.

Reproduce:

```bash
cd backend
python -m scripts.estimate_game_cost --compare --late-turn 55
```

Measured (synthetic ~210-tok narratives per prior turn; gpt-4o-mini class,
2026-08-02):

| Mode | DM input @ t1 | DM input @ t55 | Full game (60) |
|---|---:|---:|---:|
| `flat` (no prior digest) | 1466 | 1466 | **~$0.076** |
| `raw_history` | 1466 | **12870** (~+211 tok/prior turn) | **~$0.132** (O(T²) interpolate) |
| `digest` (prod) | 1622 | 1622 | **~$0.077** |

Sampling only turn 1 under `raw_history` falsely reports ~$0.076; sampling
only turn 55 and multiplying ×60 overstates at ~$0.179. The interpolate
path is the honest full-game figure when input grows with turn.

**Production mitigation:** Narrator emits `world_state_digest` in adjudication
JSON; next turn feeds it back (no extra LLM call). Soft-capped at
`WORLD_STATE_DIGEST_MAX_CHARS` (~400 tokens).

**Caveats:**
- OpenRouter list prices may differ slightly from OpenAI map rates; real
  completion lengths vary; early wins (<60 turns) cost less.
- **N seats:** each extra AI faction adds ~1 seat-move call per turn;
  Narrator prompt also grows. Frontend `costEstimate` mirrors lineup on
  the Setup screen.
- Plausibility gate + `/off` add occasional extra Narrator calls not
  included in the 180-call baseline.
- Digest quality (coherence vs drift) still needs live-LLM spot checks.
