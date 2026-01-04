"""Vertex AI (Gemini) implementation.

This module provides a concrete `LLMClient` implementation backed by Google
Vertex AI. The provider SDK is imported lazily so unit tests can run without
external dependencies.

Authentication is expected to use Application Default Credentials (ADC).
"""

from __future__ import annotations

import asyncio
import json
import threading
from dataclasses import dataclass
from typing import Any, Callable

from backend.nodes.llm.base import LLMClient, LLMResponse, LLMUsage


@dataclass(frozen=True, slots=True)
class VertexAISettings:
    project: str
    location: str


class VertexAILLMClient(LLMClient):
    """Vertex AI-backed LLM client.

    Args:
        settings: Project/location used for `vertexai.init(...)`.
        init_fn: Optional override for initialization (used in unit tests).
        model_factory: Optional override that returns a model object with a
            `generate_content(prompt, generation_config=...)` method.
    """

    def __init__(
        self,
        *,
        settings: VertexAISettings,
        init_fn: Callable[[], None] | None = None,
        model_factory: Callable[[str], Any] | None = None,
    ) -> None:
        self._settings = settings
        self._init_fn = init_fn
        self._model_factory = model_factory

        self._init_lock = threading.Lock()
        self._initialized = False

    async def complete(
        self,
        *,
        model: str,
        prompt: str,
        json_mode: bool,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> LLMResponse:
        if not isinstance(model, str) or not model:
            raise ValueError("model must be a non-empty string")
        if not isinstance(prompt, str) or not prompt:
            raise ValueError("prompt must be a non-empty string")

        self._ensure_initialized()

        generation_config: dict[str, Any] = {}
        if temperature is not None:
            generation_config["temperature"] = temperature
        if max_output_tokens is not None:
            generation_config["max_output_tokens"] = max_output_tokens
        if json_mode:
            generation_config["response_mime_type"] = "application/json"

        model_obj = self._get_model(model)

        def _call_provider() -> Any:
            if generation_config:
                return model_obj.generate_content(prompt, generation_config=generation_config)
            return model_obj.generate_content(prompt)

        raw = await asyncio.to_thread(_call_provider)

        text = getattr(raw, "text", None)
        parsed_json: Any | None = None
        if json_mode and isinstance(text, str):
            try:
                parsed_json = json.loads(text)
            except json.JSONDecodeError:
                parsed_json = None

        usage = self._extract_usage(raw)

        return LLMResponse(text=text if isinstance(text, str) else None, json=parsed_json, usage=usage, model=model)

    def _ensure_initialized(self) -> None:
        if self._initialized:
            return
        with self._init_lock:
            if self._initialized:
                return

            if self._init_fn is not None:
                self._init_fn()
            else:
                # Lazy import so unit tests can run without provider deps.
                import vertexai  # type: ignore

                vertexai.init(project=self._settings.project, location=self._settings.location)

            self._initialized = True

    def _get_model(self, model: str) -> Any:
        if self._model_factory is not None:
            return self._model_factory(model)

        # Lazy import so unit tests can run without provider deps.
        from vertexai.generative_models import GenerativeModel  # type: ignore

        return GenerativeModel(model)

    @staticmethod
    def _extract_usage(raw: Any) -> LLMUsage | None:
        usage_meta = getattr(raw, "usage_metadata", None)
        if usage_meta is None:
            return None

        input_tokens = getattr(usage_meta, "prompt_token_count", None)
        output_tokens = getattr(usage_meta, "candidates_token_count", None)

        if input_tokens is None and output_tokens is None:
            return None

        return LLMUsage(
            input_tokens=int(input_tokens) if isinstance(input_tokens, int) else None,
            output_tokens=int(output_tokens) if isinstance(output_tokens, int) else None,
        )
