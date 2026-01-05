import time

from fastapi.testclient import TestClient

from backend.main import create_app


def _graph() -> dict:
    return {
        "version": 1,
        "nodes": [
            {
                "id": "s",
                "type": "start",
                "position": {"x": 0, "y": 0},
                "size": {"width": 1, "height": 1},
                "ports": [{"id": "s:out:1", "kind": "output"}],
                "config": {"initial_state": {"a": 1}},
            },
            {
                "id": "fork",
                "type": "parallel_gate",
                "position": {"x": 0, "y": 0},
                "size": {"width": 1, "height": 1},
                "ports": [
                    {"id": "fork:in:1", "kind": "input"},
                    {"id": "fork:out:1", "kind": "output"},
                ],
                "config": {"gate": "fork", "fanout": 2, "output_key": "fork_out"},
            },
            {
                "id": "b1",
                "type": "code_executor",
                "position": {"x": 0, "y": 0},
                "size": {"width": 1, "height": 1},
                "ports": [
                    {"id": "b1:in:1", "kind": "input"},
                    {"id": "b1:out:1", "kind": "output"},
                ],
                "config": {"expression": "state['a'] + 1", "output_key": "b"},
            },
            {
                "id": "b2",
                "type": "code_executor",
                "position": {"x": 0, "y": 0},
                "size": {"width": 1, "height": 1},
                "ports": [
                    {"id": "b2:in:1", "kind": "input"},
                    {"id": "b2:out:1", "kind": "output"},
                ],
                "config": {"expression": "state['a'] + 2", "output_key": "c"},
            },
            {
                "id": "join",
                "type": "parallel_gate",
                "position": {"x": 0, "y": 0},
                "size": {"width": 1, "height": 1},
                "ports": [
                    {"id": "join:in:1", "kind": "input"},
                    {"id": "join:out:1", "kind": "output"},
                ],
                "config": {"gate": "join", "output_key": "join_out"},
            },
            {
                "id": "e",
                "type": "end",
                "position": {"x": 0, "y": 0},
                "size": {"width": 1, "height": 1},
                "ports": [{"id": "e:in:1", "kind": "input"}],
                "config": {"result_key": "result"},
            },
        ],
        "edges": [
            {
                "id": "e1",
                "from": {"nodeId": "s", "portId": "s:out:1"},
                "to": {"nodeId": "fork", "portId": "fork:in:1"},
            },
            {
                "id": "e2",
                "from": {"nodeId": "fork", "portId": "fork:out:1"},
                "to": {"nodeId": "b1", "portId": "b1:in:1"},
            },
            {
                "id": "e3",
                "from": {"nodeId": "fork", "portId": "fork:out:1"},
                "to": {"nodeId": "b2", "portId": "b2:in:1"},
            },
            {
                "id": "e4",
                "from": {"nodeId": "b1", "portId": "b1:out:1"},
                "to": {"nodeId": "join", "portId": "join:in:1"},
            },
            {
                "id": "e5",
                "from": {"nodeId": "b2", "portId": "b2:out:1"},
                "to": {"nodeId": "join", "portId": "join:in:1"},
            },
            {
                "id": "e6",
                "from": {"nodeId": "join", "portId": "join:out:1"},
                "to": {"nodeId": "e", "portId": "e:in:1"},
            },
        ],
    }


def _wait_for_run_final(client: TestClient, run_id: str, *, timeout_s: float = 1.5) -> dict:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        got = client.get(f"/api/run/{run_id}")
        assert got.status_code == 200
        data = got.json()
        if data["status"] != "running":
            return data
        time.sleep(0.01)
    raise AssertionError("run did not finish in time")


def test_run_parallel_gate_fork_parallel_join_topology() -> None:
    client = TestClient(create_app())

    run_created = client.post("/api/run", json={"graph": _graph(), "mode": "run"})
    assert run_created.status_code == 200

    final = _wait_for_run_final(client, run_created.json()["run_id"])
    assert final["status"] == "completed"

    trace = final["trace"]
    assert [s["node_id"] for s in trace] == ["s", "fork", "b1", "b2", "join", "e"]

    end_step = next(s for s in trace if s["node_id"] == "e")
    result = end_step["output"]["result"]

    assert result["b"] == 2
    assert result["c"] == 3
    assert result["fork_out"]["gate"] == "fork"
    assert result["join_out"]["gate"] == "join"
