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

    # An OpenAI key outranks OpenRouter for OpenRouter-wrapped OpenAI models.
    assert seen[0] == {"model": "openai/gpt-4o-mini", "extra": {"api_key": "oa-key"}}
    assert seen[1]["extra"] == {"api_key": "oa-key"}
    assert seen[2]["extra"] is None  # no key for this provider -> env default


async def _routes(api_keys: dict[str, str], model: str) -> dict:
    seen: dict = {}

    class _Resp:
        content = "ok"
        model = "m"
        is_dry_run = False

    async def fake_acall(m, prompt, *, system=None, constraints=None, dry_run=False):
        seen.update(model=m, extra=constraints.extra_params)
        return _Resp()

    await LlmCallClient(acall_fn=fake_acall, api_keys=api_keys).complete(model, "hi")
    return seen


async def test_direct_anthropic_key_outranks_openrouter_and_normalises_name():
    seen = await _routes(
        {"openrouter": "or", "anthropic": "an"}, "openrouter/anthropic/claude-haiku-5.5"
    )
    assert seen == {"model": "anthropic/claude-haiku-5-5", "extra": {"api_key": "an"}}


async def test_openrouter_used_when_no_direct_key_for_vendor():
    seen = await _routes({"openrouter": "or"}, "openrouter/anthropic/claude-haiku-5.5")
    assert seen == {
        "model": "openrouter/anthropic/claude-haiku-5.5",
        "extra": {"api_key": "or"},
    }


async def test_non_direct_vendor_stays_on_openrouter():
    seen = await _routes(
        {"openrouter": "or", "openai": "oa", "anthropic": "an"},
        "openrouter/deepseek/deepseek-v4.1-flash",
    )
    assert seen == {
        "model": "openrouter/deepseek/deepseek-v4.1-flash",
        "extra": {"api_key": "or"},
    }
