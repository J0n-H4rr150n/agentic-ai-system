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
        "edges": [
            {"id": "e1", "from": {"nodeId": "a", "portId": "a:out:1"}, "to": {"nodeId": "b", "portId": "b:in:1"}},
        ],
    }


def test_create_and_get_workflow_roundtrip() -> None:
    client = TestClient(create_app())

    created = client.post("/api/workflow", json={"graph": _simple_graph()})
    assert created.status_code == 200
    workflow_id = created.json()["workflow_id"]
    assert isinstance(workflow_id, str)
    assert workflow_id

    got = client.get(f"/api/workflow/{workflow_id}")
    assert got.status_code == 200
    data = got.json()

    assert data["workflow_id"] == workflow_id
    assert data["version"] == 1
    assert "created_at" in data
    assert "updated_at" in data
    assert data["graph"]["version"] == 1
    assert [n["id"] for n in data["graph"]["nodes"]] == ["a", "b"]


def test_workflow_versioning_create_list_and_get() -> None:
    client = TestClient(create_app())

    created = client.post("/api/workflow", json={"graph": _simple_graph()})
    assert created.status_code == 200
    workflow_id = created.json()["workflow_id"]

    updated_graph = {
        **_simple_graph(),
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
                "config": {"changed": True},
            },
        ],
    }

    v2 = client.post(f"/api/workflow/{workflow_id}/version", json={"graph": updated_graph})
    assert v2.status_code == 200
    assert v2.json()["workflow_id"] == workflow_id
    assert v2.json()["version"] == 2

    versions = client.get(f"/api/workflow/{workflow_id}/versions")
    assert versions.status_code == 200
    versions_data = versions.json()
    assert versions_data["workflow_id"] == workflow_id
    assert versions_data["latest_version"] == 2
    assert [v["version"] for v in versions_data["versions"]] == [1, 2]

    latest = client.get(f"/api/workflow/{workflow_id}")
    assert latest.status_code == 200
    assert latest.json()["version"] == 2
    assert latest.json()["graph"]["nodes"][1]["config"].get("changed") is True

    v1 = client.get(f"/api/workflow/{workflow_id}?version=1")
    assert v1.status_code == 200
    assert v1.json()["version"] == 1
    assert v1.json()["graph"]["nodes"][1]["config"].get("changed") is None

    unknown = client.get(f"/api/workflow/{workflow_id}?version=999")
    assert unknown.status_code == 404


def test_get_unknown_workflow_returns_404() -> None:
    client = TestClient(create_app())
    got = client.get("/api/workflow/does-not-exist")
    assert got.status_code == 404


def test_create_workflow_version_unknown_workflow_returns_404() -> None:
    client = TestClient(create_app())
    created = client.post("/api/workflow/does-not-exist/version", json={"graph": _simple_graph()})
    assert created.status_code == 404


def test_list_workflow_versions_unknown_workflow_returns_404() -> None:
    client = TestClient(create_app())
    got = client.get("/api/workflow/does-not-exist/versions")
    assert got.status_code == 404
