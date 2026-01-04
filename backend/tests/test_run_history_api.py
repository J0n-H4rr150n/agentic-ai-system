import time

from fastapi.testclient import TestClient

from backend.main import create_app
from backend.runs.store import RUN_HISTORY_STORE


def _wait_until(predicate, timeout_s: float = 2.0, interval_s: float = 0.02):
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if predicate():
            return
        time.sleep(interval_s)
    raise AssertionError("Timed out waiting for condition")


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
            {
                "id": "e1",
                "from": {"nodeId": "a", "portId": "a:out:1"},
                "to": {"nodeId": "b", "portId": "b:in:1"},
            }
        ],
    }
def test_run_history_records_terminal_run() -> None:
    RUN_HISTORY_STORE.clear()
    client = TestClient(create_app())

    create = client.post("/api/run", json={"graph": _simple_graph(), "mode": "run"})
    assert create.status_code == 200
    run_id = create.json()["run_id"]

    def _is_terminal():
        resp = client.get(f"/api/run/{run_id}")
        assert resp.status_code == 200
        return resp.json()["status"] in {"completed", "failed", "cancelled"}

    _wait_until(_is_terminal)

    # Appears in persisted run history
    lst = client.get("/api/runs")
    assert lst.status_code == 200
    data = lst.json()
    assert "runs" in data
    assert any(r["run_id"] == run_id for r in data["runs"])

    detail = client.get(f"/api/runs/{run_id}")
    assert detail.status_code == 200
    detail_json = detail.json()
    assert detail_json["run_id"] == run_id
    assert detail_json["status"] == "completed"
    assert isinstance(detail_json.get("trace"), list)


def test_run_history_list_can_filter_by_workflow_id() -> None:
    RUN_HISTORY_STORE.clear()
    client = TestClient(create_app())

    w1 = client.post("/api/workflow", json={"graph": _simple_graph()})
    assert w1.status_code == 200
    workflow_id_1 = w1.json()["workflow_id"]

    w2 = client.post("/api/workflow", json={"graph": _simple_graph()})
    assert w2.status_code == 200
    workflow_id_2 = w2.json()["workflow_id"]

    r1 = client.post("/api/run", json={"graph": _simple_graph(), "mode": "run", "workflow_id": workflow_id_1})
    assert r1.status_code == 200
    run_id_1 = r1.json()["run_id"]

    r2 = client.post("/api/run", json={"graph": _simple_graph(), "mode": "run", "workflow_id": workflow_id_2})
    assert r2.status_code == 200
    run_id_2 = r2.json()["run_id"]

    _wait_until(lambda: client.get(f"/api/run/{run_id_1}").json()["status"] != "running")
    _wait_until(lambda: client.get(f"/api/run/{run_id_2}").json()["status"] != "running")

    filtered_1 = client.get(f"/api/runs?workflow_id={workflow_id_1}")
    assert filtered_1.status_code == 200
    runs_1 = filtered_1.json()["runs"]
    assert any(r["run_id"] == run_id_1 for r in runs_1)
    assert all(r.get("workflow_id") == workflow_id_1 for r in runs_1)

    filtered_2 = client.get(f"/api/runs?workflow_id={workflow_id_2}")
    assert filtered_2.status_code == 200
    runs_2 = filtered_2.json()["runs"]
    assert any(r["run_id"] == run_id_2 for r in runs_2)
    assert all(r.get("workflow_id") == workflow_id_2 for r in runs_2)
