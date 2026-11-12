"""Rolling world_state_digest — O(T) Narrator continuity memory."""

from __future__ import annotations

from app.domain.scoring import initial_scores
from app.llm.prompts import (
    WORLD_STATE_DIGEST_MAX_CHARS,
    build_dm_prompt,
    clamp_world_state_digest,
)


ROLES = ("hwg", "defender_ai", "selfish_ai")


def test_clamp_world_state_digest_caps_length():
    assert clamp_world_state_digest(None) == ""
    assert clamp_world_state_digest("  a   b  ") == "a b"
    huge = "x" * (WORLD_STATE_DIGEST_MAX_CHARS + 50)
    out = clamp_world_state_digest(huge)
    assert len(out) <= WORLD_STATE_DIGEST_MAX_CHARS
    assert out.endswith("…")


def test_dm_prompt_includes_digest_schema_and_prior():
    scores = initial_scores(ROLES)
    _system, user = build_dm_prompt(
        turn_number=12,
        narrative_date="2027-12-01",
        current_scores=scores,
        moves={
            "hwg": "Hold.",
            "defender_ai": "Audit.",
            "selfish_ai": "Expand.",
        },
        scored_roles=ROLES,
        prior_world_state_digest="Prior digest: multipolar compute race.",
    )
    assert "world_state_digest" in user
    assert "Prior digest: multipolar compute race." in user
    assert "rolling memory" in user.lower() or "Prior world-state digest" in user


def test_dm_prompt_turn1_has_no_prior_digest_body():
    scores = initial_scores(ROLES)
    _system, user = build_dm_prompt(
        turn_number=1,
        narrative_date="2027-01-01",
        current_scores=scores,
        moves={"hwg": "Hold.", "defender_ai": "Watch.", "selfish_ai": "Probe."},
        scored_roles=ROLES,
    )
    assert "none yet" in user.lower()
    assert "world_state_digest" in user
