"""Anti-corruption layer over llmcall (preferred) or litellm (Vercel fallback)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
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

    try:
        response = await acompletion(**kwargs)
        content = response.choices[0].message.content or ""
        return LLMOutput(content=content, model=getattr(response, "model", model) or model)
    except Exception as exc:  # noqa: BLE001 — map provider failures to ACL error
        raise LLMClientError("provider_error", str(exc)) from exc


class LlmCallClient:
    """Wraps llmcall.acall when available; otherwise litellm.acompletion."""

    def __init__(self, acall_fn: AcallFn | None = None) -> None:
        self._acall = acall_fn

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
            )

        from llmcall.models import CallConstraints, LLMError

        constraints = CallConstraints(
            temperature=temperature,
            max_tokens=max_tokens,
            timeout_seconds=timeout_seconds,
            response_format=response_format,
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
