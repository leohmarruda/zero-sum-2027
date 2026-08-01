"""Domain-facing LLM types — no llmcall imports here."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol


@dataclass(frozen=True)
class LLMOutput:
    content: str
    model: str
    is_dry_run: bool = False


class LLMClientError(Exception):
    def __init__(self, error_type: str, message: str):
        self.error_type = error_type
        self.message = message
        super().__init__(f"{error_type}: {message}")


class LLMClient(Protocol):
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
    ) -> LLMOutput: ...
