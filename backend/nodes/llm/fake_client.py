"""Deterministic fake LLM client.

Used for MVP end-to-end testing without external network/provider credentials.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.nodes.llm.base import LLMClient, LLMResponse


@dataclass(slots=True)
class FakeLLMClient(LLMClient):
    """A minimal LLM client that returns deterministic output."""

    def __init__(self, *, fixed_text: str | None = None) -> None:
        self._fixed_text = fixed_text

    async def complete(
        self,
        *,
        model: str,
        prompt: str,
        json_mode: bool,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> LLMResponse:
        if json_mode:
            return LLMResponse(
                model=model,
                text=None,
                json={"findings": [], "summary": "fake"},
                usage=None,
            )

        return LLMResponse(
            model=model,
            text=self._fixed_text or "fake",
            json=None,
            usage=None,
        )
