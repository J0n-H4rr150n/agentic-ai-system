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
from collections import deque
from dataclasses import dataclass
from typing import Any

from backend.nodes.base import BaseNode, NodeExecutionError
from backend.runner.graph_parser import ExecutionPlan
from backend.runner.state import StateContainer


@dataclass(slots=True)
class AsyncExecutor:
    """Executes a graph plan using asyncio for parallel-ready nodes."""

    async def run(self, plan: ExecutionPlan, nodes: dict[str, BaseNode], state: StateContainer | None = None) -> StateContainer:
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

            tasks = {node_id: asyncio.create_task(nodes[node_id].execute(run_state.to_dict())) for node_id in batch}

            results: dict[str, dict[str, Any]] = {}
            for node_id, task in tasks.items():
                try:
                    result = await task
                except NodeExecutionError:
                    raise
                except Exception as exc:  # noqa: BLE001
                    raise NodeExecutionError(node_id=node_id, message=str(exc)) from exc

                if not isinstance(result, dict):
                    raise NodeExecutionError(node_id=node_id, message="Node output must be a dict")

                results[node_id] = result

            # Deterministic application of results independent of task completion order.
            for node_id in sorted(results):
                run_state.update(results[node_id])
                completed.add(node_id)

                for neighbor in plan.outgoing.get(node_id, []):
                    indegree[neighbor] -= 1
                    if indegree[neighbor] == 0:
                        ready.append(neighbor)

        if len(completed) != len(plan.node_ids):
            raise ValueError("Execution did not complete all nodes (cycle or missing edges)")

        return run_state
