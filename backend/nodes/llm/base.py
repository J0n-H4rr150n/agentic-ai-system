"""Provider-agnostic LLM node base interface.

This module intentionally avoids tying the codebase to any specific provider SDK.
Provider implementations (e.g., Vertex AI) should adapt their SDK responses into
`LLMResponse` and satisfy the `LLMClient` protocol.

The current runner executes nodes as `async def execute(state) -> dict`.
To keep nodes useful before config/context wiring is expanded, `LLMCallNode`
accepts a node-local config dict at construction time.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Protocol

from backend.nodes.base import BaseNode


@dataclass(slots=True)
class LLMUsage:
    """Token usage information (when available)."""

    input_tokens: int | None = None
    output_tokens: int | None = None


@dataclass(slots=True)
class LLMResponse:
    """Normalized response from an LLM provider."""

    text: str | None = None
    json: Any | None = None
    usage: LLMUsage | None = None
    model: str | None = None


class LLMClient(Protocol):
    """Provider-agnostic LLM client interface."""

    async def complete(
        self,
        *,
        model: str,
        prompt: str,
        json_mode: bool,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> LLMResponse:
        raise NotImplementedError


class LLMCallNode(BaseNode):
    """LLM call node using an injected provider client."""

    def __init__(
        self,
        node_id: str,
        *,
        client: LLMClient,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(node_id=node_id, node_type="llm")
        self._client = client
        self._config = dict(config or {})

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        model = self._require_non_empty_str(self._config, "model")
        output_key = self._config.get("output_key", "llm_output")
        if not isinstance(output_key, str) or not output_key:
            raise ValueError("LLMCallNode config.output_key must be a non-empty string")

        prompt = self._resolve_prompt(state)
        json_mode = bool(self._config.get("json_mode", False))

        temperature = self._config.get("temperature")
        if temperature is not None and not isinstance(temperature, (int, float)):
            raise ValueError("LLMCallNode config.temperature must be a number")

        max_output_tokens = self._config.get("max_output_tokens")
        if max_output_tokens is not None and not isinstance(max_output_tokens, int):
            raise ValueError("LLMCallNode config.max_output_tokens must be an int")

        response = await self._client.complete(
            model=model,
            prompt=prompt,
            json_mode=json_mode,
            temperature=float(temperature) if isinstance(temperature, (int, float)) else None,
            max_output_tokens=max_output_tokens,
        )

        normalized_json = response.json
        if json_mode and normalized_json is None and response.text is not None:
            try:
                normalized_json = json.loads(response.text)
            except json.JSONDecodeError as exc:
                raise ValueError("LLMCallNode expected JSON output but got non-JSON text") from exc

        payload = {
            "model": response.model or model,
            "text": response.text,
            "json": normalized_json,
            "usage": None if response.usage is None else {"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens},
        }
        return {output_key: payload}

    def _resolve_prompt(self, state: dict[str, Any]) -> str:
        raw_prompt = self._config.get("prompt")
        if raw_prompt is not None:
            if not isinstance(raw_prompt, str) or not raw_prompt.strip():
                raise ValueError("LLMCallNode config.prompt must be a non-empty string")
            return raw_prompt

        prompt_key = self._config.get("prompt_key")
        if prompt_key is None:
            raise ValueError("LLMCallNode requires either config.prompt or config.prompt_key")
        if not isinstance(prompt_key, str) or not prompt_key:
            raise ValueError("LLMCallNode config.prompt_key must be a non-empty string")

        value = state.get(prompt_key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"LLMCallNode state[{prompt_key!r}] must be a non-empty string")
        return value

    @staticmethod
    def _require_non_empty_str(config: dict[str, Any], key: str) -> str:
        value = config.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(f"LLMCallNode config.{key} must be a non-empty string")
        return value
