"""LLM configuration types.

The runner currently passes node `config` at construction time (not at execution
call time). This module provides typed helpers that provider implementations can
use, while keeping the wire format a plain dict for JSON serialization.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LLMConfig:
    """Basic LLM call settings."""

    model: str
    prompt: str | None = None
    prompt_key: str | None = None
    json_mode: bool = False
    temperature: float | None = None
    max_output_tokens: int | None = None
    output_key: str = "llm_output"
