from fastapi.testclient import TestClient

from backend.main import create_app


def _simple_graph() -> dict:
    return {
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
            {"id": "e1", "from": {"nodeId": "a", "portId": "a:out:1"}, "to": {"nodeId": "b", "portId": "b:in:1"}},
        ],
    }


def test_create_and_get_workflow_roundtrip() -> None:
    client = TestClient(create_app())

    created = client.post("/api/workflow", json={"graph": _simple_graph()})
    assert created.status_code == 200
    workflow_id = created.json()["workflow_id"]
    assert isinstance(workflow_id, str)
    assert workflow_id

    got = client.get(f"/api/workflow/{workflow_id}")
    assert got.status_code == 200
    data = got.json()

    assert data["workflow_id"] == workflow_id
    assert "created_at" in data
    assert "updated_at" in data
    assert data["graph"]["version"] == 1
    assert [n["id"] for n in data["graph"]["nodes"]] == ["a", "b"]


def test_get_unknown_workflow_returns_404() -> None:
    client = TestClient(create_app())
    got = client.get("/api/workflow/does-not-exist")
    assert got.status_code == 404
