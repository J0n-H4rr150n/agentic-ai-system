from fastapi.testclient import TestClient

from backend.main import create_app


def _workflow_graph() -> dict:
    return {
        "version": 1,
        "nodes": [
            {
                "id": "start",
                "type": "start",
                "position": {"x": 0, "y": 0},
                "size": {"width": 1, "height": 1},
                "ports": [{"id": "start:out:1", "kind": "output"}],
                "config": {"initial_state": {"target_url": "https://example.test/"}},
            },
            {
                "id": "browser",
                "type": "browser",
                "position": {"x": 0, "y": 0},
                "size": {"width": 1, "height": 1},
                "ports": [
                    {"id": "browser:in:1", "kind": "input"},
                    {"id": "browser:out:1", "kind": "output"},
                ],
                "config": {"action": "navigate", "url_key": "target_url", "output_key": "browser_output"},
            },
            {
                "id": "llm",
                "type": "llm",
                "position": {"x": 0, "y": 0},
                "size": {"width": 1, "height": 1},
                "ports": [
                    {"id": "llm:in:1", "kind": "input"},
                    {"id": "llm:out:1", "kind": "output"},
                ],
                "config": {
                    "model": "m",
                    "prompt": "static prompt",
                    "json_mode": True,
                    "output_key": "llm_output",
                },
            },
            {
                "id": "router",
                "type": "router",
                "position": {"x": 0, "y": 0},
                "size": {"width": 1, "height": 1},
                "ports": [
                    {"id": "router:in:1", "kind": "input"},
                    {"id": "router:out:1", "kind": "output"},
                ],
                "config": {
                    "output_key": "router_output",
                    "conditions": [
                        {
                            "var": "llm_output.json.findings",
                            "op": "contains",
                            "value": "sql",
                            "output": "found",
                        }
                    ],
                },
            },
            {
                "id": "end",
                "type": "end",
                "position": {"x": 0, "y": 0},
                "size": {"width": 1, "height": 1},
                "ports": [{"id": "end:in:1", "kind": "input"}],
                "config": {"result_key": "result"},
            },
        ],
        "edges": [
            {
                "id": "e1",
                "from": {"nodeId": "start", "portId": "start:out:1"},
                "to": {"nodeId": "browser", "portId": "browser:in:1"},
            },
            {
                "id": "e2",
                "from": {"nodeId": "browser", "portId": "browser:out:1"},
                "to": {"nodeId": "llm", "portId": "llm:in:1"},
            },
            {
                "id": "e3",
                "from": {"nodeId": "llm", "portId": "llm:out:1"},
                "to": {"nodeId": "router", "portId": "router:in:1"},
            },
            {
                "id": "e4",
                "from": {"nodeId": "router", "portId": "router:out:1"},
                "to": {"nodeId": "end", "portId": "end:in:1"},
            },
        ],
    }


def _agent_child_graph() -> dict:
    return {
        "version": 1,
        "nodes": [
            {
                "id": "cs",
                "type": "start",
                "position": {"x": 0, "y": 0},
                "size": {"width": 1, "height": 1},
                "ports": [{"id": "cs:out:1", "kind": "output"}],
                "config": {"initial_state": {"child_out": 1}},
            },
            {
                "id": "ce",
                "type": "end",
                "position": {"x": 0, "y": 0},
                "size": {"width": 1, "height": 1},
                "ports": [{"id": "ce:in:1", "kind": "input"}],
                "config": {"result_key": "child_result"},
            },
        ],
        "edges": [
            {
                "id": "ce1",
                "from": {"nodeId": "cs", "portId": "cs:out:1"},
                "to": {"nodeId": "ce", "portId": "ce:in:1"},
            }
        ],
    }


def _agent_parent_graph(child_workflow_id: str) -> dict:
    return {
        "version": 1,
        "nodes": [
            {
                "id": "ps",
                "type": "start",
                "position": {"x": 0, "y": 0},
                "size": {"width": 1, "height": 1},
                "ports": [{"id": "ps:out:1", "kind": "output"}],
                "config": {},
            },
            {
                "id": "agent",
                "type": "agent",
                "position": {"x": 0, "y": 0},
                "size": {"width": 1, "height": 1},
                "ports": [
                    {"id": "agent:in:1", "kind": "input"},
                    {"id": "agent:out:1", "kind": "output"},
                ],
                "config": {"workflow_id": child_workflow_id},
            },
            {
                "id": "pe",
                "type": "end",
                "position": {"x": 0, "y": 0},
                "size": {"width": 1, "height": 1},
                "ports": [{"id": "pe:in:1", "kind": "input"}],
                "config": {"result_key": "result"},
            },
        ],
        "edges": [
            {
                "id": "pe1",
                "from": {"nodeId": "ps", "portId": "ps:out:1"},
                "to": {"nodeId": "agent", "portId": "agent:in:1"},
            },
            {
                "id": "pe2",
                "from": {"nodeId": "agent", "portId": "agent:out:1"},
                "to": {"nodeId": "pe", "portId": "pe:in:1"},
            },
        ],
    }


def test_workflow_schema_infers_inputs_and_outputs() -> None:
    client = TestClient(create_app())

    created = client.post("/api/workflow", json={"graph": _workflow_graph()})
    assert created.status_code == 200
    workflow_id = created.json()["workflow_id"]

    resp = client.get(f"/api/workflow/{workflow_id}/schema")
    assert resp.status_code == 200
    body = resp.json()

    assert body["workflow_id"] == workflow_id
    assert body["version"] == 1

    # Inputs: browser reads target_url, router condition reads llm_output.*
    assert body["inputs"] == ["llm_output", "target_url"]

    # Outputs: known output keys + start injected key + end result.
    assert body["outputs"] == ["browser_output", "llm_output", "result", "router_output", "target_url"]
    assert body["warnings"] == []


def test_workflow_schema_includes_agent_nested_outputs() -> None:
    client = TestClient(create_app())

    child = client.post("/api/workflow", json={"graph": _agent_child_graph()})
    assert child.status_code == 200
    child_id = child.json()["workflow_id"]

    parent = client.post("/api/workflow", json={"graph": _agent_parent_graph(child_id)})
    assert parent.status_code == 200
    parent_id = parent.json()["workflow_id"]

    resp = client.get(f"/api/workflow/{parent_id}/schema")
    assert resp.status_code == 200
    body = resp.json()

    # Parent outputs include agent boundary + nested workflow outputs.
    assert "__agent__" in body["outputs"]
    assert "child_out" in body["outputs"]
    assert "child_result" in body["outputs"]
    assert "result" in body["outputs"]
