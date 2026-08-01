# docs/prompts/PROMPT_CONTEXT_zero-sum-2027.md
#
# Goal: Turn Service orchestrates collect human move → generate AI moves in
# parallel → DM adjudicate → domain normalize → persist → evaluate outcome.
#
# Pattern: Service orchestration · Repository for persistence · async/await ·
# DIP (domain/llm injected, not imported as concrete globals where avoidable).
#
# Do:
# - Blind turns: AI move generation must not see peer move_text for the
#   current turn.
# - Idempotent resolve if turn already adjudicated.
# - Persist ScoreSnapshot (normalized) + DMAdjudication (incl. raw).
# - On win/draw set Game.status=ended, winner, ended_at.
#
# Don't:
# - Skip normalize_turn_scores before persist.
# - Expose other seats' current-turn moves to the human client on submit.
#
# Done when: integration test with mocked LLM runs turn 1→N to win or draw
# without breaking sum=100.
