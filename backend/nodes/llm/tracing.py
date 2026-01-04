"""LLM tracing helpers.

This module focuses on trace data that is useful for observability:
- token usage (input/output)
- elapsed time (ms)
- decision capture fields

The runner already captures per-node execution time in `StepTrace`. This trace
is LLM-specific and should travel with the LLM output payload.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class UsageLike(Protocol):
    input_tokens: int | None
    output_tokens: int | None


@dataclass(frozen=True, slots=True)
class LLMTrace:
    input_tokens: int | None
    output_tokens: int | None
    elapsed_time_ms: int
    llm_decision: str | None = None
    llm_reasoning: str | None = None
    llm_confidence: float | None = None


def build_llm_trace(*, usage: UsageLike | None, elapsed_time_ms: int, payload_json: Any | None) -> LLMTrace:
    """Build an `LLMTrace` from optional usage data and payload JSON.

    Args:
        usage: Token usage info when provided by the provider.
        elapsed_time_ms: Wall-clock time spent in provider call.
        payload_json: Parsed JSON payload (if any) used for decision extraction.

    Returns:
        LLMTrace with best-effort decision extraction.
    """

    input_tokens = usage.input_tokens if usage is not None else None
    output_tokens = usage.output_tokens if usage is not None else None

    decision, reasoning, confidence = extract_decision_fields(payload_json)

    return LLMTrace(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        elapsed_time_ms=int(elapsed_time_ms),
        llm_decision=decision,
        llm_reasoning=reasoning,
        llm_confidence=confidence,
    )


def extract_decision_fields(payload_json: Any | None) -> tuple[str | None, str | None, float | None]:
    """Extract decision fields from a JSON response payload.

    This is intentionally conservative: it only extracts from dict-like JSON.

    Recognized keys:
    - decision / llm_decision
    - reasoning / llm_reasoning
    - confidence / llm_confidence

    Confidence is coerced to float when possible.
    """

    if not isinstance(payload_json, dict):
        return None, None, None

    decision = payload_json.get("llm_decision", payload_json.get("decision"))
    reasoning = payload_json.get("llm_reasoning", payload_json.get("reasoning"))
    confidence = payload_json.get("llm_confidence", payload_json.get("confidence"))

    if decision is not None and not isinstance(decision, str):
        decision = str(decision)

    if reasoning is not None and not isinstance(reasoning, str):
        reasoning = str(reasoning)

    if confidence is None:
        confidence_f = None
    elif isinstance(confidence, (int, float)):
        confidence_f = float(confidence)
    else:
        try:
            confidence_f = float(confidence)
        except (TypeError, ValueError):
            confidence_f = None

    return decision if isinstance(decision, str) else None, reasoning if isinstance(reasoning, str) else None, confidence_f
