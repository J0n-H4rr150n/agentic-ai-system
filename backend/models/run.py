"""Run/trace data models.

These models represent execution traces produced by the runner.

MVP scope: step-level tracing for node execution.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


StepStatus = Literal["ok", "error"]


class StepTrace(BaseModel):
    """A single node execution trace record."""

    step_id: int = Field(ge=1)
    node_id: str = Field(min_length=1)
    input: dict[str, Any]
    output: dict[str, Any] | None = None
    duration_ms: int = Field(ge=0)
    status: StepStatus
    error: str | None = None
