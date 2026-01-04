import time

from fastapi.testclient import TestClient

from backend.main import create_app


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


def test_pause_run_persists_checkpoint(monkeypatch) -> None:
    # Monkeypatch node factory in the run route module to ensure execution takes
    # long enough to issue a pause request deterministically.
    from backend.api.routes import run as run_routes
    from backend.nodes.base import BaseNode

    class SleepNode(BaseNode):
        def __init__(self, node_id: str, sleep_s: float) -> None:
            super().__init__(node_id=node_id, node_type="sleep")
            self._sleep_s = sleep_s

        async def execute(self, state: dict[str, object]) -> dict[str, object]:
            import asyncio

            await asyncio.sleep(self._sleep_s)
            return {"slept": True}

    class PassthroughStart(BaseNode):
        def __init__(self, node_id: str) -> None:
            super().__init__(node_id=node_id, node_type="start")

        async def execute(self, state: dict[str, object]) -> dict[str, object]:
            return {}

    class PassthroughEnd(BaseNode):
        def __init__(self, node_id: str) -> None:
            super().__init__(node_id=node_id, node_type="end")

        async def execute(self, state: dict[str, object]) -> dict[str, object]:
            return {"done": True}

    def _fake_build_nodes_for_graph(*, run_id: str, graph_nodes: list[object]):
        # Keep ids matching the graph.
        return {
            "a": PassthroughStart("a"),
            "b": SleepNode("b", sleep_s=0.2),
            "c": PassthroughEnd("c"),
        }

    monkeypatch.setattr(run_routes, "build_nodes_for_graph", _fake_build_nodes_for_graph)

    client = TestClient(create_app())

    created = client.post("/api/run", json={"graph": _pauseable_graph(), "mode": "run"})
    assert created.status_code == 200
    run_id = created.json()["run_id"]

    paused = client.post(f"/api/run/{run_id}/pause")
    assert paused.status_code == 200

    final = None
    for _ in range(100):
        got = client.get(f"/api/run/{run_id}")
        assert got.status_code == 200
        data = got.json()
        if data["status"] != "running":
            final = data
            break
        time.sleep(0.01)

    assert final is not None
    assert final["status"] == "paused"
    assert isinstance(final["trace"], list)
    assert final.get("paused_at") is not None

    checkpoint = client.get(f"/api/run/{run_id}/checkpoint")
    assert checkpoint.status_code == 200
    ck = checkpoint.json()
    assert ck["run_id"] == run_id
    assert isinstance(ck["state"], dict)
    assert isinstance(ck["completed_node_ids"], list)
    assert isinstance(ck["ready_node_ids"], list)
    assert isinstance(ck["indegree"], dict)


def test_pause_then_resume_completes_run(monkeypatch) -> None:
    from backend.api.routes import run as run_routes
    from backend.nodes.base import BaseNode

    class SleepNode(BaseNode):
        def __init__(self, node_id: str, sleep_s: float) -> None:
            super().__init__(node_id=node_id, node_type="sleep")
            self._sleep_s = sleep_s

        async def execute(self, state: dict[str, object]) -> dict[str, object]:
            import asyncio

            await asyncio.sleep(self._sleep_s)
            return {"slept": True}

    class PassthroughStart(BaseNode):
        def __init__(self, node_id: str) -> None:
            super().__init__(node_id=node_id, node_type="start")

        async def execute(self, state: dict[str, object]) -> dict[str, object]:
            return {}

    class PassthroughEnd(BaseNode):
        def __init__(self, node_id: str) -> None:
            super().__init__(node_id=node_id, node_type="end")

        async def execute(self, state: dict[str, object]) -> dict[str, object]:
            return {"done": True}

    def _fake_build_nodes_for_graph(*, run_id: str, graph_nodes: list[object]):
        return {
            "a": PassthroughStart("a"),
            "b": SleepNode("b", sleep_s=0.05),
            "c": PassthroughEnd("c"),
        }

    monkeypatch.setattr(run_routes, "build_nodes_for_graph", _fake_build_nodes_for_graph)

    client = TestClient(create_app())
    created = client.post("/api/run", json={"graph": _pauseable_graph(), "mode": "run"})
    assert created.status_code == 200
    run_id = created.json()["run_id"]

    paused = client.post(f"/api/run/{run_id}/pause")
    assert paused.status_code == 200

    for _ in range(200):
        got = client.get(f"/api/run/{run_id}")
        assert got.status_code == 200
        data = got.json()
        if data["status"] == "paused":
            break
        time.sleep(0.01)

    resumed = client.post(f"/api/run/{run_id}/resume")
    assert resumed.status_code == 200

    final = None
    for _ in range(200):
        got = client.get(f"/api/run/{run_id}")
        assert got.status_code == 200
        data = got.json()
        if data["status"] != "running":
            final = data
            break
        time.sleep(0.01)

    assert final is not None
    assert final["status"] == "completed"
    assert [s["node_id"] for s in final["trace"]] == ["a", "b", "c"]
    assert [s["step_id"] for s in final["trace"]] == [1, 2, 3]
