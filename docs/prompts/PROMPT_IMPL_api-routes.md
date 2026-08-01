# docs/prompts/PROMPT_CONTEXT_zero-sum-2027.md
#
# Goal: implement REST routes from spec.md §2.11 with unified error envelope
# {"error": {"code": str, "message": str}}.
#
# Pattern: REST + OpenAPI · thin presentation layer calling services ·
# validation via Pydantic.
#
# Routes:
# - POST /games
# - GET /games/{id}
# - POST /games/{id}/turns/{n}/moves
# - POST /games/{id}/turns/{n}/resolve
# - GET /games/{id}/turns/{n}
# - GET /games/{id}/history
#
# MVP seat rule (Open Gate 2.13, provisional): humanity=human;
# rogue_ai/defender_ai/dm=ai unless explicitly overridden later.
#
# Done when: routes return real payloads (not 501 stubs); OpenAPI reflects
# schemas; error envelope consistent on 4xx/404.
