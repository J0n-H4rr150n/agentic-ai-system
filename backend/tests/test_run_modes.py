import time

from fastapi.testclient import TestClient

from backend.main import create_app


def _wait_for_terminal(client: TestClient, run_id: str, *, timeout_s: float = 3.0) -> dict:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        resp = client.get(f"/api/run/{run_id}")
        assert resp.status_code == 200
        data = resp.json()
        if data["status"] in {"completed", "failed", "cancelled"}:
            return data
        time.sleep(0.01)
    raise AssertionError("run did not reach terminal state")


def test_test_mode_stubs_http_request() -> None:
    client = TestClient(create_app())

    graph = {
        "nodes": [
            {"id": "start", "type": "start", "config": {}},
            {"id": "h", "type": "http_request", "config": {"method": "POST", "url": "https://example.test/"}},
            {"id": "end", "type": "end", "config": {}},
        ],
        "edges": [
            {"id": "e1", "from_node": "start", "to_node": "h"},
            {"id": "e2", "from_node": "h", "to_node": "end"},
        ],
    }

    created = client.post("/api/run", json={"graph": graph, "mode": "test"})
    assert created.status_code == 200

    status = _wait_for_terminal(client, created.json()["run_id"])
    assert status["status"] == "completed"

    http_steps = [s for s in status["trace"] if s["node_id"] == "h"]
    assert len(http_steps) == 1
    out = http_steps[0]["output"]["http_output"]
    assert out["mode"] == "test"
    assert out["status"] == 200


def test_simulate_mode_blocks_side_effecting_http_methods() -> None:
    client = TestClient(create_app())

    graph = {
        "nodes": [
            {"id": "start", "type": "start", "config": {}},
            {"id": "h", "type": "http_request", "config": {"method": "POST", "url": "https://example.test/"}},
            {"id": "end", "type": "end", "config": {}},
        ],
        "edges": [
            {"id": "e1", "from_node": "start", "to_node": "h"},
            {"id": "e2", "from_node": "h", "to_node": "end"},
        ],
    }

    created = client.post("/api/run", json={"graph": graph, "mode": "simulate"})
    assert created.status_code == 200

    status = _wait_for_terminal(client, created.json()["run_id"])
    assert status["status"] == "failed"
    assert "simulate mode" in (status.get("error") or "")
