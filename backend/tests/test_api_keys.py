"""Per-request provider API keys: header parsing and per-call routing."""

from __future__ import annotations

from app.api.deps import api_keys_from_headers
from app.llm.client import LlmCallClient


def test_headers_parsed_for_known_providers_only():
    keys = api_keys_from_headers(
        {
            "X-Api-Key-Openrouter": "  sk-or-1  ",
            "x-api-key-openai": "sk-oa",
            "X-Api-Key-Evil": "nope",
            "X-Api-Key-Anthropic": "",
            "Authorization": "Bearer x",
        }
    )
    assert keys == {"openrouter": "sk-or-1", "openai": "sk-oa"}


def test_oversized_key_is_ignored():
    assert api_keys_from_headers({"X-Api-Key-Openai": "k" * 513}) == {}


async def test_key_chosen_by_model_provider_and_passed_per_call():
    seen: list[dict] = []

    class _Resp:
        content = "ok"
        model = "m"
        is_dry_run = False

    async def fake_acall(model, prompt, *, system=None, constraints=None, dry_run=False):
        seen.append({"model": model, "extra": constraints.extra_params})
        return _Resp()

    client = LlmCallClient(
        acall_fn=fake_acall, api_keys={"openrouter": "or-key", "openai": "oa-key"}
    )
    await client.complete("openrouter/openai/gpt-4o-mini", "hi")
    await client.complete("openai/gpt-4o-mini", "hi")
    await client.complete("anthropic/claude-x", "hi")

    assert seen[0]["extra"] == {"api_key": "or-key"}
    assert seen[1]["extra"] == {"api_key": "oa-key"}
    assert seen[2]["extra"] is None  # no key for this provider -> env default
