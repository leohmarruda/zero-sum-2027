"""Anti-corruption layer over llmcall (preferred) or litellm (Vercel fallback)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from typing import TYPE_CHECKING, Any, Literal

from app.llm.types import LLMClientError, LLMOutput

if TYPE_CHECKING:
    from llmcall.models import LLMError, LLMResponse

AcallFn = Callable[..., Awaitable["LLMResponse | LLMError"]]


def _import_acall() -> AcallFn | None:
    try:
        from llmcall import acall
    except ImportError:
        return None
    return acall


async def _complete_via_litellm(
    model: str,
    prompt: str,
    *,
    system: str | None,
    temperature: float | None,
    max_tokens: int | None,
    response_format: Literal["text", "json"],
    timeout_seconds: float,
    dry_run: bool,
    api_key: str | None = None,
) -> LLMOutput:
    if dry_run:
        return LLMOutput(content="", model=model, is_dry_run=True)

    try:
        from litellm import acompletion
    except ImportError as exc:
        raise ImportError(
            "Neither llmcall nor litellm is installed. "
            "Local: pip install -e ../../llmcall  |  Vercel: litellm in requirements.txt"
        ) from exc

    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    kwargs: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "timeout": timeout_seconds,
    }
    if temperature is not None:
        kwargs["temperature"] = temperature
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    if response_format == "json":
        kwargs["response_format"] = {"type": "json_object"}
    if api_key:
        kwargs["api_key"] = api_key

    try:
        response = await acompletion(**kwargs)
        content = response.choices[0].message.content or ""
        return LLMOutput(content=content, model=getattr(response, "model", model) or model)
    except Exception as exc:  # noqa: BLE001 — map provider failures to ACL error
        raise LLMClientError("provider_error", str(exc)) from exc


API_KEY_PROVIDERS: frozenset[str] = frozenset({"openrouter", "openai", "anthropic"})

# Vendors that can be reached directly. When the user supplies such a key, a
# model written as "openrouter/<vendor>/<name>" is sent straight to the vendor.
DIRECT_VENDORS: frozenset[str] = frozenset({"openai", "anthropic"})


class LlmCallClient:
    """Wraps llmcall.acall when available; otherwise litellm.acompletion.

    `api_keys` maps provider -> key for this client only (per request). The key is
    chosen by the model's provider prefix and passed per call — never exported to
    the process environment, so concurrent requests cannot see each other's keys.
    """

    def __init__(
        self,
        acall_fn: AcallFn | None = None,
        api_keys: Mapping[str, str] | None = None,
    ) -> None:
        self._acall = acall_fn
        self._api_keys = dict(api_keys or {})

    def _key_for(self, model: str) -> str | None:
        provider = model.split("/", 1)[0].lower()
        return self._api_keys.get(provider) or None

    def _route(self, model: str) -> tuple[str, str | None]:
        """Return (model, api_key) to use for this call.

        Direct OpenAI/Anthropic keys take priority over OpenRouter: if the model
        is an OpenRouter-wrapped OpenAI/Anthropic model and the user supplied
        that vendor's key, rewrite it to the native model name and use the key.
        """
        provider, _, rest = model.partition("/")
        if provider.lower() == "openrouter":
            vendor, _, name = rest.partition("/")
            vendor = vendor.lower()
            if name and vendor in DIRECT_VENDORS and self._api_keys.get(vendor):
                if vendor == "anthropic":
                    # OpenRouter slugs use dots (claude-haiku-5.5); Anthropic's
                    # native ids use dashes (claude-haiku-5-5).
                    name = name.replace(".", "-")
                return f"{vendor}/{name}", self._api_keys[vendor]
        return model, self._key_for(model)

    async def complete(
        self,
        model: str,
        prompt: str,
        *,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        response_format: Literal["text", "json"] = "text",
        timeout_seconds: float = 60.0,
        dry_run: bool = False,
    ) -> LLMOutput:
        model, api_key = self._route(model)
        acall_fn = self._acall if self._acall is not None else _import_acall()
        if acall_fn is None:
            return await _complete_via_litellm(
                model,
                prompt,
                system=system,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format,
                timeout_seconds=timeout_seconds,
                dry_run=dry_run,
                api_key=api_key,
            )

        from llmcall.models import CallConstraints, LLMError

        constraints = CallConstraints(
            temperature=temperature,
            max_tokens=max_tokens,
            timeout_seconds=timeout_seconds,
            response_format=response_format,
            extra_params={"api_key": api_key} if api_key else None,
        )
        result = await acall_fn(
            model,
            prompt,
            system=system,
            constraints=constraints,
            dry_run=dry_run,
        )
        if isinstance(result, LLMError):
            raise LLMClientError(result.error_type, result.message)
        return LLMOutput(
            content=result.content,
            model=result.model,
            is_dry_run=result.is_dry_run,
        )
