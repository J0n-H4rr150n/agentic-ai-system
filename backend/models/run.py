"""Run/trace data models.

These models represent execution traces produced by the runner.

MVP scope: step-level tracing for node execution.
"""

from __future__ import annotations

from datetime import datetime
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


class RunCheckpoint(BaseModel):
    """A persisted checkpoint captured at a safe pause boundary."""

    run_id: str = Field(min_length=1)
    created_at: datetime
    state: dict[str, Any]
    completed_node_ids: list[str]
    ready_node_ids: list[str]
    indegree: dict[str, int]
    handled_interrupts: list[str] = Field(default_factory=list)
