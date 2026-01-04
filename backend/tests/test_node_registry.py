import pytest

from backend.models.graph import GraphDefinition
from backend.nodes.registry import NodeRegistry
from backend.runner.graph_parser import parse_graph


def test_node_registry_discover_registers_expected_types() -> None:
    registry = NodeRegistry()
    registry.discover()

    for node_type in ["start", "end", "router", "browser", "llm", "http_request", "code_executor"]:
        assert registry.is_supported(node_type)


def test_node_registry_discover_is_idempotent() -> None:
    registry = NodeRegistry()
    registry.discover()
    first = registry.list_all()
    registry.discover()
    second = registry.list_all()
    assert first == second


def test_parse_graph_accepts_router_and_http_request_types() -> None:
    graph = GraphDefinition(
        nodes=[
            {
                "id": "n1",
                "type": "start",
                "position": {"x": 0, "y": 0},
                "size": {"width": 100, "height": 50},
                "ports": [],
                "config": {},
            },
            {
                "id": "n2",
                "type": "http_request",
                "position": {"x": 0, "y": 0},
                "size": {"width": 100, "height": 50},
                "ports": [],
                "config": {"method": "GET", "url": "https://example.test"},
            },
            {
                "id": "n3",
                "type": "router",
                "position": {"x": 0, "y": 0},
                "size": {"width": 100, "height": 50},
                "ports": [],
                "config": {"conditions": []},
            },
        ],
        edges=[
            {"id": "e1", "from": {"nodeId": "n1", "portId": "out"}, "to": {"nodeId": "n2", "portId": "in"}},
            {"id": "e2", "from": {"nodeId": "n2", "portId": "out"}, "to": {"nodeId": "n3", "portId": "in"}},
        ],
    )

    plan = parse_graph(graph)
    assert plan.node_ids == ["n1", "n2", "n3"]


def test_parse_graph_accepts_code_executor_type() -> None:
    graph = GraphDefinition(
        nodes=[
            {
                "id": "n1",
                "type": "start",
                "position": {"x": 0, "y": 0},
                "size": {"width": 100, "height": 50},
                "ports": [],
                "config": {"initial_state": {"a": 2}},
            },
            {
                "id": "n2",
                "type": "code_executor",
                "position": {"x": 0, "y": 0},
                "size": {"width": 100, "height": 50},
                "ports": [],
                "config": {"expression": "state['a'] + 1", "output_key": "b"},
            },
        ],
        edges=[
            {"id": "e1", "from": {"nodeId": "n1", "portId": "out"}, "to": {"nodeId": "n2", "portId": "in"}},
        ],
    )

    plan = parse_graph(graph)
    assert plan.node_ids == ["n1", "n2"]


def test_parse_graph_rejects_unknown_type() -> None:
    graph = GraphDefinition(
        nodes=[
            {
                "id": "n1",
                "type": "not_a_real_node",
                "position": {"x": 0, "y": 0},
                "size": {"width": 100, "height": 50},
                "ports": [],
                "config": {},
            }
        ],
        edges=[],
    )

    with pytest.raises(ValueError, match="Unsupported node type"):
        parse_graph(graph)
