"""Async executor.

Executes an ExecutionPlan respecting dependencies.

Design goals for MVP:
- Parallel execution: run all currently-ready nodes concurrently via asyncio.
- Determinism: stable ready ordering and deterministic application of outputs.
- Testability: keep this module small and dependency-free.

Tracing and streaming are handled in later stories.
"""

from __future__ import annotations

import asyncio
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Callable

from backend.nodes.base import BaseNode, NodeExecutionError
from backend.runner.graph_parser import ExecutionPlan
from backend.runner.state import StateContainer
from backend.runner.tracer import StepTracer


@dataclass(frozen=True, slots=True)
class ExecutionCheckpoint:
    """Serializable checkpoint data captured at a safe executor boundary."""

    state: dict[str, Any]
    completed_node_ids: list[str]
    ready_node_ids: list[str]
    indegree: dict[str, int]


class RunPaused(Exception):
    """Raised by the executor when a pause is requested at a safe boundary."""

    def __init__(self, checkpoint: ExecutionCheckpoint) -> None:
        super().__init__("Run paused")
        self.checkpoint = checkpoint


@dataclass(slots=True)
class AsyncExecutor:
    """Executes a graph plan using asyncio for parallel-ready nodes."""

    async def run(
        self,
        plan: ExecutionPlan,
        nodes: dict[str, BaseNode],
        state: StateContainer | None = None,
        tracer: StepTracer | None = None,
        should_pause: Callable[[], bool] | None = None,
    ) -> StateContainer:
        """Execute the plan.

        Args:
            plan: Parsed ExecutionPlan (adjacency lists).
            nodes: Mapping of node_id -> BaseNode.
            state: Optional initial state container.

        Returns:
            The final StateContainer.

        Raises:
            ValueError: If nodes are missing for ids in the plan.
            NodeExecutionError: If a node execution fails.
        """

        missing = [node_id for node_id in plan.node_ids if node_id not in nodes]
        if missing:
            raise ValueError(f"Missing node implementations for: {sorted(missing)}")

        run_state = state or StateContainer()

        indegree: dict[str, int] = {node_id: len(plan.incoming.get(node_id, [])) for node_id in plan.node_ids}
        ready = deque([node_id for node_id in plan.node_ids if indegree.get(node_id, 0) == 0])

        completed: set[str] = set()

        while ready:
            batch = sorted(ready)
            ready.clear()

            batch_input = run_state.to_dict()
            start_times = {node_id: time.perf_counter() for node_id in batch}
            tasks = [asyncio.create_task(nodes[node_id].execute(dict(batch_input))) for node_id in batch]
            raw_results = await asyncio.gather(*tasks, return_exceptions=True)

            results: dict[str, dict[str, Any]] = {}
            errors: dict[str, NodeExecutionError] = {}

            for node_id, raw in zip(batch, raw_results, strict=True):
                duration_ms = int(round((time.perf_counter() - start_times[node_id]) * 1000))

                if isinstance(raw, Exception):
                    if isinstance(raw, NodeExecutionError):
                        err = raw
                    else:
                        err = NodeExecutionError(node_id=node_id, message=str(raw))
                    errors[node_id] = err
                    if tracer is not None:
                        tracer.record(
                            node_id=node_id,
                            input=batch_input,
                            output=None,
                            duration_ms=duration_ms,
                            status="error",
                            error=str(err),
                        )
                    continue

                if not isinstance(raw, dict):
                    err = NodeExecutionError(node_id=node_id, message="Node output must be a dict")
                    errors[node_id] = err
                    if tracer is not None:
                        tracer.record(
                            node_id=node_id,
                            input=batch_input,
                            output=None,
                            duration_ms=duration_ms,
                            status="error",
                            error=str(err),
                        )
                    continue

                results[node_id] = raw
                if tracer is not None:
                    tracer.record(
                        node_id=node_id,
                        input=batch_input,
                        output=raw,
                        duration_ms=duration_ms,
                        status="ok",
                        error=None,
                    )

            # Deterministic application of results independent of task completion order.
            for node_id in sorted(results):
                run_state.update(results[node_id])
                completed.add(node_id)

                for neighbor in plan.outgoing.get(node_id, []):
                    indegree[neighbor] -= 1
                    if indegree[neighbor] == 0:
                        ready.append(neighbor)

            if should_pause is not None and should_pause():
                raise RunPaused(
                    ExecutionCheckpoint(
                        state=run_state.to_dict(),
                        completed_node_ids=sorted(completed),
                        ready_node_ids=sorted(ready),
                        indegree=dict(indegree),
                    )
                )

            if errors:
                first = sorted(errors)[0]
                raise errors[first]

        if len(completed) != len(plan.node_ids):
            raise ValueError("Execution did not complete all nodes (cycle or missing edges)")

        return run_state
