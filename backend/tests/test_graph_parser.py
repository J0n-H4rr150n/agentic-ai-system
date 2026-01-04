import pytest

from backend.models.graph import GraphDefinition
from backend.nodes.registry import NodeRegistry
from backend.runner.graph_parser import parse_graph


def test_parse_graph_builds_adjacency() -> None:
    graph = GraphDefinition.model_validate(
        {
            "version": 1,
            "nodes": [
                {
                    "id": "a",
                    "type": "start",
                    "position": {"x": 0, "y": 0},
                    "size": {"width": 1, "height": 1},
                    "ports": [{"id": "a:out:1", "kind": "output"}],
                    "config": {},
                },
                {
                    "id": "b",
                    "type": "end",
                    "position": {"x": 0, "y": 0},
                    "size": {"width": 1, "height": 1},
                    "ports": [{"id": "b:in:1", "kind": "input"}],
                    "config": {},
                },
            ],
            "edges": [
                {"id": "e1", "from": {"nodeId": "a", "portId": "a:out:1"}, "to": {"nodeId": "b", "portId": "b:in:1"}}
            ],
        }
    )

    plan = parse_graph(graph)
    assert plan.node_ids == ["a", "b"]
    assert plan.outgoing == {"a": ["b"], "b": []}
    assert plan.incoming == {"a": [], "b": ["a"]}


def test_parse_graph_rejects_unknown_node_type() -> None:
    graph = GraphDefinition.model_validate(
        {
            "version": 1,
            "nodes": [
                {
                    "id": "a",
                    "type": "weird",
                    "position": {"x": 0, "y": 0},
                    "size": {"width": 1, "height": 1},
                    "ports": [],
                    "config": {},
                }
            ],
            "edges": [],
        }
    )

    registry = NodeRegistry(allowed_types={"start"})
    with pytest.raises(ValueError, match="Unsupported node type"):
        parse_graph(graph, registry=registry)
