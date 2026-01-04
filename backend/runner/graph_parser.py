"""Graph parser.

Converts a validated GraphDefinition into a runner-friendly ExecutionPlan.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from backend.models.graph import GraphDefinition, InterruptConfig
from backend.nodes.registry import NodeRegistry


@dataclass(frozen=True, slots=True)
class ExecutionPlan:
    node_ids: list[str]
    outgoing: dict[str, list[str]]
    incoming: dict[str, list[str]]
    interrupts: dict[str, InterruptConfig] = field(default_factory=dict)


def parse_graph(graph: GraphDefinition, registry: NodeRegistry | None = None) -> ExecutionPlan:
    """Build an execution plan from a GraphDefinition.

    The execution plan is intentionally lightweight:
    - node_ids: stable list of node ids
    - outgoing/incoming adjacency lists for fast traversal

    Raises:
        ValueError: if the graph contains unsupported node types.
    """

    registry = registry or NodeRegistry()
    registry.discover()

    for node in graph.nodes:
        if not registry.is_supported(node.type):
            raise ValueError(f"Unsupported node type: {node.type}")

    node_ids = [n.id for n in graph.nodes]
    outgoing = {node_id: [] for node_id in node_ids}
    incoming = {node_id: [] for node_id in node_ids}

    for edge in graph.edges:
        src = edge.from_.nodeId
        dst = edge.to.nodeId
        outgoing[src].append(dst)
        incoming[dst].append(src)

    # Deterministic ordering for testability.
    for node_id in node_ids:
        outgoing[node_id] = sorted(outgoing[node_id])
        incoming[node_id] = sorted(incoming[node_id])

    interrupts: dict[str, InterruptConfig] = {}
    for node in graph.nodes:
        if node.interrupt is not None:
            interrupts[node.id] = node.interrupt

    return ExecutionPlan(node_ids=node_ids, outgoing=outgoing, incoming=incoming, interrupts=interrupts)
