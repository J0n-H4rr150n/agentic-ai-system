"""Dependency resolution utilities.

This module computes deterministic execution orders over a directed acyclic graph (DAG).
"""

from __future__ import annotations

from collections import deque

from backend.runner.graph_parser import ExecutionPlan


def topological_sort(plan: ExecutionPlan) -> list[str]:
    """Return a deterministic topological ordering of the plan.

    Raises:
        ValueError: if the graph contains a cycle.
    """

    indegree: dict[str, int] = {node_id: len(plan.incoming.get(node_id, [])) for node_id in plan.node_ids}

    # Use a queue seeded in stable node_ids order for determinism.
    ready = deque([node_id for node_id in plan.node_ids if indegree.get(node_id, 0) == 0])

    order: list[str] = []
    outgoing = plan.outgoing

    while ready:
        node_id = ready.popleft()
        order.append(node_id)

        for neighbor in outgoing.get(node_id, []):
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                ready.append(neighbor)

    if len(order) != len(plan.node_ids):
        raise ValueError("Graph contains a cycle")

    return order
