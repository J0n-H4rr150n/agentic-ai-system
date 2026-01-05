import time

from fastapi.testclient import TestClient

from backend.main import create_app


def _child_workflow_graph() -> dict:
    return {
        "version": 1,
        "nodes": [
            {
                "id": "sa",
                "type": "start",
                "position": {"x": 0, "y": 0},
                "size": {"width": 1, "height": 1},
                "ports": [{"id": "sa:out:1", "kind": "output"}],
                "config": {},
            },
            {
                "id": "sb",
                "type": "code_executor",
                "position": {"x": 0, "y": 0},
                "size": {"width": 1, "height": 1},
                "ports": [
                    {"id": "sb:in:1", "kind": "input"},
                    {"id": "sb:out:1", "kind": "output"},
                ],
                "config": {
                    "expression": "state['loop_iteration'] >= 3",
                    "output_key": "should_break",
                },
            },
            {
                "id": "sc",
                "type": "end",
                "position": {"x": 0, "y": 0},
                "size": {"width": 1, "height": 1},
                "ports": [{"id": "sc:in:1", "kind": "input"}],
                "config": {},
            },
        ],
        "edges": [
            {
                "id": "se1",
                "from": {"nodeId": "sa", "portId": "sa:out:1"},
                "to": {"nodeId": "sb", "portId": "sb:in:1"},
            },
            {
                "id": "se2",
                "from": {"nodeId": "sb", "portId": "sb:out:1"},
                "to": {"nodeId": "sc", "portId": "sc:in:1"},
            },
        ],
    }


def _parent_graph(workflow_id: str, *, max_iterations: int = 10) -> dict:
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
                "id": "loop1",
                "type": "loop",
                "position": {"x": 0, "y": 0},
                "size": {"width": 1, "height": 1},
                "ports": [
                    {"id": "loop1:in:1", "kind": "input"},
                    {"id": "loop1:out:1", "kind": "output"},
                ],
                "config": {
                    "workflow_id": workflow_id,
                    "break_key": "should_break",
                    "max_iterations": max_iterations,
                },
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
            {
                "id": "e1",
                "from": {"nodeId": "a", "portId": "a:out:1"},
                "to": {"nodeId": "loop1", "portId": "loop1:in:1"},
            },
            {
                "id": "e2",
                "from": {"nodeId": "loop1", "portId": "loop1:out:1"},
                "to": {"nodeId": "b", "portId": "b:in:1"},
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


def test_run_loop_node_repeats_child_workflow_until_break() -> None:
    client = TestClient(create_app())

    created = client.post("/api/workflow", json={"graph": _child_workflow_graph()})
    assert created.status_code == 200
    workflow_id = created.json()["workflow_id"]

    run_created = client.post("/api/run", json={"graph": _parent_graph(workflow_id), "mode": "run"})
    assert run_created.status_code == 200

    final = _wait_for_run_final(client, run_created.json()["run_id"])
    assert final["status"] == "completed"

    trace = final["trace"]
    assert [s["node_id"] for s in trace] == ["a", "loop1", "b"]

    loop_step = next(s for s in trace if s["node_id"] == "loop1")
    assert loop_step["status"] == "ok"
    assert loop_step["output"]["loop_iteration"] == 3
    assert loop_step["output"]["should_break"] is True

    meta = loop_step["output"]["__loop__"]
    assert meta["workflow_id"] == workflow_id
    assert meta["iterations"] == 3
    assert meta["stopped_reason"] == "break"


def test_run_loop_node_stops_at_max_iterations_when_never_breaks() -> None:
    client = TestClient(create_app())

    created = client.post("/api/workflow", json={"graph": _child_workflow_graph()})
    assert created.status_code == 200
    workflow_id = created.json()["workflow_id"]

    run_created = client.post(
        "/api/run",
        json={"graph": _parent_graph(workflow_id, max_iterations=2), "mode": "run"},
    )
    assert run_created.status_code == 200

    final = _wait_for_run_final(client, run_created.json()["run_id"])
    assert final["status"] == "completed"

    loop_step = next(s for s in final["trace"] if s["node_id"] == "loop1")
    meta = loop_step["output"]["__loop__"]
    assert meta["iterations"] == 2
    assert meta["stopped_reason"] == "max_iterations"
