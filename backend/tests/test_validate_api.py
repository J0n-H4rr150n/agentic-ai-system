from fastapi.testclient import TestClient

from backend.main import create_app


def test_validate_endpoint_accepts_valid_graph() -> None:
    client = TestClient(create_app())

    graph = {
        "nodes": [
            {"id": "start", "type": "start", "config": {}},
            {"id": "end", "type": "end", "config": {}},
        ],
        "edges": [{"id": "e1", "from_node": "start", "to_node": "end"}],
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
            {"id": "a", "type": "start", "config": {}},
            {"id": "b", "type": "router", "config": {"conditions": []}},
        ],
        "edges": [
            {"id": "e1", "from_node": "a", "to_node": "b"},
            {"id": "e2", "from_node": "b", "to_node": "a"},
        ],
    }

    resp = client.post("/api/validate", json={"graph": graph})
    assert resp.status_code == 400
    assert "cycle" in resp.json()["detail"].lower()
