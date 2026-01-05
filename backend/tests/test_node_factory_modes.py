import asyncio

import pytest

from backend.models.graph import GraphDefinition
from backend.runner.mode_guard import GuardedNode
from backend.runner.node_factory import build_nodes_for_graph


def _graph_with_node(node_type: str, config: dict) -> GraphDefinition:
    return GraphDefinition(
        nodes=[
            {
                "id": "start",
                "type": "start",
                "position": {"x": 0, "y": 0},
                "size": {"width": 100, "height": 50},
                "ports": [],
                "config": {},
            },
            {
                "id": "n",
                "type": node_type,
                "position": {"x": 0, "y": 0},
                "size": {"width": 100, "height": 50},
                "ports": [],
                "config": config,
            },
        ],
        edges=[
            {"id": "e1", "from": {"nodeId": "start", "portId": "out"}, "to": {"nodeId": "n", "portId": "in"}},
        ],
    )


def test_node_factory_wraps_http_request_in_simulate_guard() -> None:
    graph = _graph_with_node("http_request", {"method": "POST", "url": "https://example.test/"})
    nodes = build_nodes_for_graph(run_id="r1", graph_nodes=graph.nodes, mode="simulate")

    guarded = nodes["n"]
    assert isinstance(guarded, GuardedNode)

    with pytest.raises(ValueError, match="simulate mode"):
        asyncio.run(guarded.execute({}))


def test_node_factory_wraps_http_fuzzer_in_simulate_guard() -> None:
    graph = _graph_with_node(
        "http_fuzzer",
        {"method": "POST", "url_template": "https://example.test/?q={payload}", "payloads": ["a"]},
    )
    nodes = build_nodes_for_graph(run_id="r1", graph_nodes=graph.nodes, mode="simulate")

    guarded = nodes["n"]
    assert isinstance(guarded, GuardedNode)

    with pytest.raises(ValueError, match="simulate mode"):
        asyncio.run(guarded.execute({}))
