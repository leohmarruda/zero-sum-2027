"""Anti-corruption layer over llmcall."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Literal

from app.llm.types import LLMClientError, LLMOutput

if TYPE_CHECKING:
    from llmcall.models import LLMError, LLMResponse

AcallFn = Callable[..., Awaitable["LLMResponse | LLMError"]]


def _import_acall() -> AcallFn:
    try:
        from llmcall import acall
    except ImportError as exc:
        raise ImportError(
            "llmcall is not installed. From backend run:\n"
            '  pip install -e "../../llmcall"'
        ) from exc
    return acall


class LlmCallClient:
    """Wraps llmcall.acall; services depend on the LLMClient protocol."""

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
        acall_fn = self._acall or _import_acall()
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
