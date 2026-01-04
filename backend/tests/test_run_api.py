import time

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
        "edges": [{"id": "e1", "from": {"nodeId": "a", "portId": "a:out:1"}, "to": {"nodeId": "b", "portId": "b:in:1"}}],
    }


def test_post_run_creates_run_and_get_returns_status_and_trace() -> None:
    client = TestClient(create_app())

    resp = client.post("/api/run", json={"graph": _simple_graph(), "mode": "run"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "running"
    run_id = body["run_id"]

    # Background execution should complete quickly; poll briefly.
    final = None
    for _ in range(50):
        got = client.get(f"/api/run/{run_id}")
        assert got.status_code == 200
        data = got.json()
        if data["status"] != "running":
            final = data
            break
        time.sleep(0.01)

    assert final is not None
    assert final["status"] == "completed"
    assert isinstance(final["trace"], list)
    assert [s["node_id"] for s in final["trace"]] == ["a", "b"]


def test_get_run_404_for_unknown_id() -> None:
    client = TestClient(create_app())

    resp = client.get("/api/run/does-not-exist")
    assert resp.status_code == 404
