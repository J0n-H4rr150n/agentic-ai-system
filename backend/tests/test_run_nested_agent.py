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
                "config": {"initial_state": {"merged": "yes"}},
            },
            {
                "id": "sb",
                "type": "end",
                "position": {"x": 0, "y": 0},
                "size": {"width": 1, "height": 1},
                "ports": [{"id": "sb:in:1", "kind": "input"}],
                "config": {},
            },
        ],
        "edges": [
            {
                "id": "se1",
                "from": {"nodeId": "sa", "portId": "sa:out:1"},
                "to": {"nodeId": "sb", "portId": "sb:in:1"},
            }
        ],
    }


def _parent_graph(workflow_id: str) -> dict:
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
                "id": "agent1",
                "type": "agent",
                "position": {"x": 0, "y": 0},
                "size": {"width": 1, "height": 1},
                "ports": [
                    {"id": "agent1:in:1", "kind": "input"},
                    {"id": "agent1:out:1", "kind": "output"},
                ],
                "config": {"workflow_id": workflow_id},
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
                "to": {"nodeId": "agent1", "portId": "agent1:in:1"},
            },
            {
                "id": "e2",
                "from": {"nodeId": "agent1", "portId": "agent1:out:1"},
                "to": {"nodeId": "b", "portId": "b:in:1"},
            },
        ],
    }


def test_run_agent_node_executes_child_workflow_and_includes_child_trace() -> None:
    client = TestClient(create_app())

    created = client.post("/api/workflow", json={"graph": _child_workflow_graph()})
    assert created.status_code == 200
    workflow_id = created.json()["workflow_id"]

    run_created = client.post("/api/run", json={"graph": _parent_graph(workflow_id), "mode": "run"})
    assert run_created.status_code == 200
    run_id = run_created.json()["run_id"]

    final = None
    for _ in range(80):
        got = client.get(f"/api/run/{run_id}")
        assert got.status_code == 200
        data = got.json()
        if data["status"] != "running":
            final = data
            break
        time.sleep(0.01)

    assert final is not None
    assert final["status"] == "completed"

    trace = final["trace"]
    assert [s["node_id"] for s in trace] == ["a", "agent1", "b"]

    agent_step = next(s for s in trace if s["node_id"] == "agent1")
    assert agent_step["status"] == "ok"
    assert agent_step["output"]["merged"] == "yes"

    meta = agent_step["output"]["__agent__"]
    assert meta["workflow_id"] == workflow_id
    assert isinstance(meta["trace"], list)
    assert [s["node_id"] for s in meta["trace"]] == ["sa", "sb"]
