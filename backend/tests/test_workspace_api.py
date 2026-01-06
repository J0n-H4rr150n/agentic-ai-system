from fastapi.testclient import TestClient

from backend.main import create_app


def test_create_and_get_workspace_roundtrip() -> None:
    client = TestClient(create_app())

    created = client.post("/api/workspace", json={"name": "My Workspace", "state": {"hello": "world"}})
    assert created.status_code == 200
    workspace_id = created.json()["workspace_id"]
    assert isinstance(workspace_id, str)
    assert workspace_id

    got = client.get(f"/api/workspace/{workspace_id}")
    assert got.status_code == 200
    data = got.json()

    assert data["workspace_id"] == workspace_id
    assert data["name"] == "My Workspace"
    assert data["version"] == 1
    assert data["state"] == {"hello": "world"}
    assert "created_at" in data
    assert "updated_at" in data


def test_list_workspaces_includes_created_workspace() -> None:
    client = TestClient(create_app())

    created = client.post("/api/workspace", json={"name": "List Me", "state": {"x": 1}})
    assert created.status_code == 200
    workspace_id = created.json()["workspace_id"]

    listed = client.get("/api/workspace")
    assert listed.status_code == 200
    data = listed.json()
    assert "workspaces" in data

    match = next((w for w in data["workspaces"] if w["workspace_id"] == workspace_id), None)
    assert match is not None
    assert match["name"] == "List Me"
    assert match["latest_version"] >= 1


def test_workspace_versioning_create_list_and_get() -> None:
    client = TestClient(create_app())

    created = client.post("/api/workspace", json={"name": "V1", "state": {"v": 1}})
    assert created.status_code == 200
    workspace_id = created.json()["workspace_id"]

    v2 = client.post(
        f"/api/workspace/{workspace_id}/version",
        json={"name": "V2", "state": {"v": 2, "nested": {"ok": True}}},
    )
    assert v2.status_code == 200
    assert v2.json()["workspace_id"] == workspace_id
    assert v2.json()["version"] == 2

    versions = client.get(f"/api/workspace/{workspace_id}/versions")
    assert versions.status_code == 200
    versions_data = versions.json()
    assert versions_data["workspace_id"] == workspace_id
    assert versions_data["latest_version"] == 2
    assert [v["version"] for v in versions_data["versions"]] == [1, 2]

    latest = client.get(f"/api/workspace/{workspace_id}")
    assert latest.status_code == 200
    assert latest.json()["version"] == 2
    assert latest.json()["name"] == "V2"
    assert latest.json()["state"]["v"] == 2

    v1 = client.get(f"/api/workspace/{workspace_id}?version=1")
    assert v1.status_code == 200
    assert v1.json()["version"] == 1
    assert v1.json()["state"]["v"] == 1

    unknown = client.get(f"/api/workspace/{workspace_id}?version=999")
    assert unknown.status_code == 404


def test_get_unknown_workspace_returns_404() -> None:
    client = TestClient(create_app())
    got = client.get("/api/workspace/does-not-exist")
    assert got.status_code == 404


def test_create_workspace_version_unknown_workspace_returns_404() -> None:
    client = TestClient(create_app())
    created = client.post("/api/workspace/does-not-exist/version", json={"state": {"a": 1}})
    assert created.status_code == 404


def test_list_workspace_versions_unknown_workspace_returns_404() -> None:
    client = TestClient(create_app())
    got = client.get("/api/workspace/does-not-exist/versions")
    assert got.status_code == 404
