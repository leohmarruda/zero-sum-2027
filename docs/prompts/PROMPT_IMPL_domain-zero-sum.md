# docs/prompts/PROMPT_CONTEXT_zero-sum-2027.md
#
# Goal: implement pure domain rules for zero-sum normalization, streaks, and
# win/draw evaluation. No I/O, no FastAPI, no SQLAlchemy.
#
# Pattern: Domain layer (DIP) · Result/Either not required for pure functions ·
# ADR-004 proportional normalization · AAA unit tests.
#
# Do:
# - Keep `app/domain/` free of infrastructure imports.
# - Guarantee each category sums to exactly 100 after normalize.
# - Humanity win only from turn >= humanity_win_turn (default 30).
# - Win = composite >= 0.9 for 10 consecutive resolved turns.
# - Draw at turn_cap if nobody won.
#
# Don't:
# - Call LLMs or touch the database from domain.
# - Trust raw LLM arithmetic without normalize_turn_scores.
#
# Done when: `pytest tests/test_domain.py` passes; assert_zero_sum holds for
# initial_scores and all normalize fixtures including degenerate inputs.
