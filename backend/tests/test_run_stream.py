import json

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


def test_run_stream_emits_steps_and_finishes() -> None:
    client = TestClient(create_app())

    created = client.post("/api/run", json={"graph": _simple_graph(), "mode": "run"})
    assert created.status_code == 200
    run_id = created.json()["run_id"]

    seen_steps: list[str] = []
    final_status: str | None = None

    with client.stream("GET", f"/api/run/{run_id}/stream") as resp:
        assert resp.status_code == 200

        current_event: str | None = None
        for raw in resp.iter_lines():
            if not raw:
                continue

            if raw.startswith("event: "):
                current_event = raw.removeprefix("event: ")
                continue

            if raw.startswith("data: ") and current_event is not None:
                payload = json.loads(raw.removeprefix("data: "))

                if current_event == "hello":
                    continue

                if current_event == "step":
                    seen_steps.append(payload["node_id"])

                if current_event == "status" and payload.get("status") in {"completed", "failed"}:
                    final_status = payload["status"]
                    break

    assert final_status == "completed"
    assert seen_steps == ["a", "b"]
