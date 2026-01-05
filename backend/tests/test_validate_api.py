from fastapi.testclient import TestClient

from backend.main import create_app


def _node(node_id: str, node_type: str, *, config: dict | None = None) -> dict:
    return {
        "id": node_id,
        "type": node_type,
        "position": {"x": 0, "y": 0},
        "size": {"width": 100, "height": 50},
        "ports": [],
        "config": config or {},
    }


def test_validate_endpoint_accepts_valid_graph() -> None:
    client = TestClient(create_app())

    graph = {
        "nodes": [
            _node("start", "start"),
            _node("end", "end"),
        ],
        "edges": [
            {"id": "e1", "from": {"nodeId": "start", "portId": "out"}, "to": {"nodeId": "end", "portId": "in"}},
        ],
    }

    resp = client.post("/api/validate", json={"graph": graph})
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert data["details"]["node_count"] == 2
    assert data["details"]["edge_count"] == 1


def test_validate_endpoint_rejects_cycle() -> None:
    client = TestClient(create_app())

    graph = {
        "nodes": [
            _node("a", "start"),
            _node("b", "router", config={"conditions": []}),
        ],
        "edges": [
            {"id": "e1", "from": {"nodeId": "a", "portId": "out"}, "to": {"nodeId": "b", "portId": "in"}},
            {"id": "e2", "from": {"nodeId": "b", "portId": "out"}, "to": {"nodeId": "a", "portId": "in"}},
        ],
    }

    resp = client.post("/api/validate", json={"graph": graph})
    assert resp.status_code == 400
    assert "cycle" in resp.json()["detail"].lower()
