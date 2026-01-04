import time

from fastapi.testclient import TestClient

from backend.main import create_app


def _interrupt_before_graph() -> dict:
    # start -> llm -> end, with an interrupt BEFORE node b
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
                "interrupt": {"before": True, "after": False, "reason": "Approve b"},
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


def test_interrupt_before_pauses_then_allow_resumes(monkeypatch) -> None:
    from backend.api.routes import run as run_routes
    from backend.nodes.base import BaseNode

    class StartNode(BaseNode):
        def __init__(self, node_id: str) -> None:
            super().__init__(node_id=node_id, node_type="start")

        async def execute(self, state: dict[str, object]) -> dict[str, object]:
            return {}

    class WorkNode(BaseNode):
        def __init__(self, node_id: str, sleep_s: float) -> None:
            super().__init__(node_id=node_id, node_type="work")
            self._sleep_s = sleep_s

        async def execute(self, state: dict[str, object]) -> dict[str, object]:
            import asyncio

            await asyncio.sleep(self._sleep_s)
            return {"b": 1}

    class EndNode(BaseNode):
        def __init__(self, node_id: str) -> None:
            super().__init__(node_id=node_id, node_type="end")

        async def execute(self, state: dict[str, object]) -> dict[str, object]:
            return {"done": True}

    def _fake_build_nodes_for_graph(*, run_id: str, graph_nodes: list[object]):
        return {"a": StartNode("a"), "b": WorkNode("b", sleep_s=0.05), "c": EndNode("c")}

    monkeypatch.setattr(run_routes, "build_nodes_for_graph", _fake_build_nodes_for_graph)

    client = TestClient(create_app())
    created = client.post("/api/run", json={"graph": _interrupt_before_graph(), "mode": "run"})
    assert created.status_code == 200
    run_id = created.json()["run_id"]

    paused = None
    for _ in range(200):
        got = client.get(f"/api/run/{run_id}")
        assert got.status_code == 200
        data = got.json()
        if data["status"] == "paused":
            paused = data
            break
        time.sleep(0.01)

    assert paused is not None
    assert paused["pause_reason"] == "interrupt"
    assert paused["pending_interrupt"]["node_id"] == "b"
    assert paused["pending_interrupt"]["phase"] == "before"
    assert [s["node_id"] for s in paused["trace"]] == ["a"]

    allowed = client.post(f"/api/run/{run_id}/hitl/allow")
    assert allowed.status_code == 200

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


def test_interrupt_edit_applies_state_patch_then_resumes(monkeypatch) -> None:
    from backend.api.routes import run as run_routes
    from backend.nodes.base import BaseNode, NodeExecutionError

    class StartNode(BaseNode):
        def __init__(self, node_id: str) -> None:
            super().__init__(node_id=node_id, node_type="start")

        async def execute(self, state: dict[str, object]) -> dict[str, object]:
            return {}

    class NeedsTokenNode(BaseNode):
        def __init__(self, node_id: str) -> None:
            super().__init__(node_id=node_id, node_type="needs_token")

        async def execute(self, state: dict[str, object]) -> dict[str, object]:
            if "token" not in state:
                raise NodeExecutionError(node_id=self.node_id, message="missing token")
            return {"token_seen": state["token"]}

    class EndNode(BaseNode):
        def __init__(self, node_id: str) -> None:
            super().__init__(node_id=node_id, node_type="end")

        async def execute(self, state: dict[str, object]) -> dict[str, object]:
            return {"done": True}

    def _fake_build_nodes_for_graph(*, run_id: str, graph_nodes: list[object]):
        return {"a": StartNode("a"), "b": NeedsTokenNode("b"), "c": EndNode("c")}

    monkeypatch.setattr(run_routes, "build_nodes_for_graph", _fake_build_nodes_for_graph)

    client = TestClient(create_app())
    created = client.post("/api/run", json={"graph": _interrupt_before_graph(), "mode": "run"})
    assert created.status_code == 200
    run_id = created.json()["run_id"]

    for _ in range(200):
        got = client.get(f"/api/run/{run_id}")
        assert got.status_code == 200
        data = got.json()
        if data["status"] == "paused":
            break
        time.sleep(0.01)

    edited = client.post(f"/api/run/{run_id}/hitl/edit", json={"state_patch": {"token": "ok"}})
    assert edited.status_code == 200

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
    outputs = {s["node_id"]: s["output"] for s in final["trace"]}
    assert outputs["b"]["token_seen"] == "ok"


def test_interrupt_reject_cancels_and_blocks_resume(monkeypatch) -> None:
    from backend.api.routes import run as run_routes
    from backend.nodes.base import BaseNode

    class StartNode(BaseNode):
        def __init__(self, node_id: str) -> None:
            super().__init__(node_id=node_id, node_type="start")

        async def execute(self, state: dict[str, object]) -> dict[str, object]:
            return {}

    class WorkNode(BaseNode):
        def __init__(self, node_id: str) -> None:
            super().__init__(node_id=node_id, node_type="work")

        async def execute(self, state: dict[str, object]) -> dict[str, object]:
            return {"b": 1}

    class EndNode(BaseNode):
        def __init__(self, node_id: str) -> None:
            super().__init__(node_id=node_id, node_type="end")

        async def execute(self, state: dict[str, object]) -> dict[str, object]:
            return {"done": True}

    def _fake_build_nodes_for_graph(*, run_id: str, graph_nodes: list[object]):
        return {"a": StartNode("a"), "b": WorkNode("b"), "c": EndNode("c")}

    monkeypatch.setattr(run_routes, "build_nodes_for_graph", _fake_build_nodes_for_graph)

    client = TestClient(create_app())
    created = client.post("/api/run", json={"graph": _interrupt_before_graph(), "mode": "run"})
    assert created.status_code == 200
    run_id = created.json()["run_id"]

    for _ in range(200):
        got = client.get(f"/api/run/{run_id}")
        assert got.status_code == 200
        data = got.json()
        if data["status"] == "paused":
            break
        time.sleep(0.01)

    rejected = client.post(f"/api/run/{run_id}/hitl/reject")
    assert rejected.status_code == 200

    got = client.get(f"/api/run/{run_id}")
    assert got.status_code == 200
    data = got.json()
    assert data["status"] == "cancelled"

    resume = client.post(f"/api/run/{run_id}/resume")
    assert resume.status_code == 409
