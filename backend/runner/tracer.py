"""Step tracing utilities.

The runner emits step-level trace records (input/output/duration/status) for each
node execution.

Tracing is designed to be:
- lightweight (simple append-only list)
- deterministic (executor controls record ordering)
- easy to serialize (Pydantic StepTrace models)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from backend.models.run import StepTrace


@dataclass(slots=True)
class StepTracer:
    """Collects step-level trace records for a single run."""

    _steps: list[StepTrace] = field(default_factory=list)
    _next_step_id: int = 1
    on_record: Callable[[StepTrace], None] | None = None

    @classmethod
    def from_existing(cls, steps: list[StepTrace], *, on_record: Callable[[StepTrace], None] | None = None) -> "StepTracer":
        """Create a tracer seeded with existing steps.

        Used to continue step_id numbering deterministically across pause/resume.
        """

        seeded = list(steps)
        next_id = len(seeded) + 1
        return cls(_steps=seeded, _next_step_id=next_id, on_record=on_record)

    def record(
        self,
        *,
        node_id: str,
        input: dict[str, Any],
        output: dict[str, Any] | None,
        duration_ms: int,
        status: str,
        error: str | None = None,
    ) -> None:
        step = StepTrace(
            step_id=self._next_step_id,
            node_id=node_id,
            input=dict(input),
            output=dict(output) if output is not None else None,
            duration_ms=duration_ms,
            status=status,  # pydantic validates
            error=error,
        )
        self._steps.append(step)
        if self.on_record is not None:
            self.on_record(step)
        self._next_step_id += 1

    def steps(self) -> list[StepTrace]:
        return list(self._steps)
