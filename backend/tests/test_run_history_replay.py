import time

from fastapi.testclient import TestClient

from backend.main import create_app
from backend.runs.store import RUN_HISTORY_STORE


def _wait_until(predicate, timeout_s: float = 2.5, interval_s: float = 0.02):
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if predicate():
            return
        time.sleep(interval_s)
    raise AssertionError("Timed out waiting for condition")


def _pauseable_graph() -> dict:
    # start -> llm -> end (llm node will be monkeypatched to sleep)
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
                "type": "llm",
                "position": {"x": 0, "y": 0},
                "size": {"width": 1, "height": 1},
                "ports": [
                    {"id": "b:in:1", "kind": "input"},
                    {"id": "b:out:1", "kind": "output"},
                ],
                "config": {"prompt": "hi", "json_mode": True},
            },
            {
                "id": "c",
                "type": "end",
                "position": {"x": 0, "y": 0},
                "size": {"width": 1, "height": 1},
                "ports": [{"id": "c:in:1", "kind": "input"}],
                "config": {},
            },
        ],
        "edges": [
            {"id": "e1", "from": {"nodeId": "a", "portId": "a:out:1"}, "to": {"nodeId": "b", "portId": "b:in:1"}},
            {"id": "e2", "from": {"nodeId": "b", "portId": "b:out:1"}, "to": {"nodeId": "c", "portId": "c:in:1"}},
        ],
    }


def test_run_history_replay_from_checkpoint(monkeypatch) -> None:
    from backend.api.routes import run as run_routes
    from backend.nodes.base import BaseNode

    RUN_HISTORY_STORE.clear()

    class SleepNode(BaseNode):
        def __init__(self, node_id: str, sleep_s: float) -> None:
            super().__init__(node_id=node_id, node_type="sleep")
            self._sleep_s = sleep_s

        async def execute(self, state: dict[str, object]) -> dict[str, object]:
            import asyncio

            await asyncio.sleep(self._sleep_s)
            return {f"done_{self.node_id}": True}

    def _fake_build_nodes_for_graph(*, run_id: str, graph_nodes: list[object]):
        # Make the first node slow enough to reliably land cancel.
        return {
            "a": SleepNode("a", sleep_s=0.12),
            "b": SleepNode("b", sleep_s=0.05),
            "c": SleepNode("c", sleep_s=0.01),
        }

    monkeypatch.setattr(run_routes, "build_nodes_for_graph", _fake_build_nodes_for_graph)

    client = TestClient(create_app())

    wf = client.post("/api/workflow", json={"graph": _pauseable_graph()})
    assert wf.status_code == 200
    workflow_id = wf.json()["workflow_id"]

    created = client.post("/api/run", json={"graph": _pauseable_graph(), "mode": "run", "workflow_id": workflow_id})
    assert created.status_code == 200
    run_id = created.json()["run_id"]

    cancelled = client.post(f"/api/run/{run_id}/cancel")
    assert cancelled.status_code == 200

    _wait_until(lambda: client.get(f"/api/run/{run_id}").json()["status"] != "running")

    hist = client.get(f"/api/runs/{run_id}")
    assert hist.status_code == 200
    hist_json = hist.json()
    assert hist_json["run_id"] == run_id
    assert hist_json["status"] == "cancelled"
    assert hist_json.get("checkpoint") is not None

    replayed = client.post(f"/api/runs/{run_id}/replay")
    assert replayed.status_code == 200
    new_run_id = replayed.json()["run_id"]
    assert new_run_id != run_id

    _wait_until(lambda: client.get(f"/api/run/{new_run_id}").json()["status"] != "running")

    final = client.get(f"/api/run/{new_run_id}")
    assert final.status_code == 200
    final_json = final.json()
    assert final_json["status"] in {"completed", "failed", "cancelled"}

    # Should not re-run node 'a' because checkpoint marked it completed.
    node_ids = [s["node_id"] for s in final_json.get("trace", [])]
    assert "a" not in node_ids

    lst = client.get(f"/api/runs?workflow_id={workflow_id}")
    assert lst.status_code == 200
    assert any(r["run_id"] == new_run_id for r in lst.json()["runs"]) and any(
        r["run_id"] == run_id for r in lst.json()["runs"]
    )
