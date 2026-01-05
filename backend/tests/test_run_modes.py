import time

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


def _edge(edge_id: str, from_id: str, to_id: str) -> dict:
    return {
        "id": edge_id,
        "from": {"nodeId": from_id, "portId": "out"},
        "to": {"nodeId": to_id, "portId": "in"},
    }


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
            _node("start", "start"),
            _node("h", "http_request", config={"method": "POST", "url": "https://example.test/"}),
            _node("end", "end"),
        ],
        "edges": [
            _edge("e1", "start", "h"),
            _edge("e2", "h", "end"),
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
            _node("start", "start"),
            _node("h", "http_request", config={"method": "POST", "url": "https://example.test/"}),
            _node("end", "end"),
        ],
        "edges": [
            _edge("e1", "start", "h"),
            _edge("e2", "h", "end"),
        ],
    }

    created = client.post("/api/run", json={"graph": graph, "mode": "simulate"})
    assert created.status_code == 200

    status = _wait_for_terminal(client, created.json()["run_id"])
    assert status["status"] == "failed"
    assert "simulate mode" in (status.get("error") or "")


def test_test_mode_stubs_http_fuzzer() -> None:
    client = TestClient(create_app())

    graph = {
        "nodes": [
            _node("start", "start"),
            {
                **_node(
                    "f",
                    "http_fuzzer",
                    config={
                        "method": "GET",
                        "url_template": "https://example.test/?q={payload}",
                        "payloads": ["a", "b"],
                    },
                ),
            },
            _node("end", "end"),
        ],
        "edges": [
            _edge("e1", "start", "f"),
            _edge("e2", "f", "end"),
        ],
    }

    created = client.post("/api/run", json={"graph": graph, "mode": "test"})
    assert created.status_code == 200

    status = _wait_for_terminal(client, created.json()["run_id"])
    assert status["status"] == "completed"

    steps = [s for s in status["trace"] if s["node_id"] == "f"]
    assert len(steps) == 1
    out = steps[0]["output"]["http_fuzzer_output"]
    assert out["mode"] == "test"
    assert out["summary"]["total"] == 2


def test_simulate_mode_blocks_side_effecting_http_fuzzer_methods() -> None:
    client = TestClient(create_app())

    graph = {
        "nodes": [
            _node("start", "start"),
            {
                **_node(
                    "f",
                    "http_fuzzer",
                    config={
                        "method": "POST",
                        "url_template": "https://example.test/?q={payload}",
                        "payloads": ["a"],
                    },
                ),
            },
            _node("end", "end"),
        ],
        "edges": [
            _edge("e1", "start", "f"),
            _edge("e2", "f", "end"),
        ],
    }

    created = client.post("/api/run", json={"graph": graph, "mode": "simulate"})
    assert created.status_code == 200

    status = _wait_for_terminal(client, created.json()["run_id"])
    assert status["status"] == "failed"
    assert "simulate mode" in (status.get("error") or "")
