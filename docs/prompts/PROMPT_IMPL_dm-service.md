# docs/prompts/PROMPT_CONTEXT_zero-sum-2027.md
#
# Goal: anti-corruption layer in `app/llm` + DM Service that builds the
# adjudication prompt, calls llmcall, parses structured JSON, and returns
# domain types (never provider shapes).
#
# Pattern: Anti-Corruption Layer · typed errors at service boundary ·
# move_text isolated as quoted narrative content (security task M2.14).
#
# Do:
# - Request JSON: world_narrative, seat_feedback, per-category scores for
#   rogue_ai/defender_ai/humanity.
# - Pass raw_llm_response through for persistence/audit.
# - One retry on invalid JSON; then deterministic fallback (keep prior scores,
#   generic "communication failure" narrative) — log as needed.
#
# Don't:
# - Let LiteLLM/OpenRouter types leak into domain or repositories.
# - Concatenate human move_text into system instructions without quoting.
#
# Done when: unit/integration tests with stubbed llmcall return parsed
# domain scores; injection attempts documented later via
# PROMPT_SECURITY_prompt-injection.md.
