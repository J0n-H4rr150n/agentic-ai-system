import pytest

from backend.models.graph import GraphDefinition


def test_graph_definition_parses_valid_graph() -> None:
    graph = GraphDefinition.model_validate(
        {
            "version": 1,
            "nodes": [
                {
                    "id": "a",
                    "type": "start",
                    "title": "Start",
                    "position": {"x": 10, "y": 20},
                    "size": {"width": 180, "height": 72},
                    "ports": [{"id": "a:out:1", "kind": "output"}],
                    "config": {"k": "v"},
                },
                {
                    "id": "b",
                    "type": "end",
                    "position": {"x": 110, "y": 220},
                    "size": {"width": 180, "height": 72},
                    "ports": [{"id": "b:in:1", "kind": "input"}],
                    "config": {},
                },
            ],
            "edges": [
                {
                    "id": "e1",
                    "from": {"nodeId": "a", "portId": "a:out:1"},
                    "to": {"nodeId": "b", "portId": "b:in:1"},
                }
            ],
        }
    )

    assert graph.nodes[0].title == "Start"
    assert graph.edges[0].from_.nodeId == "a"


def test_graph_definition_rejects_duplicate_node_ids() -> None:
    with pytest.raises(ValueError, match="Node ids must be unique"):
        GraphDefinition.model_validate(
            {
                "version": 1,
                "nodes": [
                    {
                        "id": "a",
                        "type": "t",
                        "position": {"x": 0, "y": 0},
                        "size": {"width": 1, "height": 1},
                        "ports": [],
                        "config": {},
                    },
                    {
                        "id": "a",
                        "type": "t",
                        "position": {"x": 0, "y": 0},
                        "size": {"width": 1, "height": 1},
                        "ports": [],
                        "config": {},
                    },
                ],
                "edges": [],
            }
        )


def test_graph_definition_rejects_edge_referencing_missing_node() -> None:
    with pytest.raises(ValueError, match="references missing"):
        GraphDefinition.model_validate(
            {
                "version": 1,
                "nodes": [
                    {
                        "id": "a",
                        "type": "t",
                        "position": {"x": 0, "y": 0},
                        "size": {"width": 1, "height": 1},
                        "ports": [{"id": "a:out:1", "kind": "output"}],
                        "config": {},
                    }
                ],
                "edges": [
                    {
                        "id": "e1",
                        "from": {"nodeId": "a", "portId": "a:out:1"},
                        "to": {"nodeId": "missing", "portId": "x"},
                    }
                ],
            }
        )
