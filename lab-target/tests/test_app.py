from fastapi.testclient import TestClient

from app.main import app


def test_health() -> None:
    client = TestClient(app)
    resp = client.get("/api/health")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["ok"] is True
    assert payload["service"] == "lab-target"


def test_search_escapes() -> None:
    client = TestClient(app)
    resp = client.get("/search", params={"q": "<script>alert(1)</script>"})
    assert resp.status_code == 200
    payload = resp.json()
    assert "<" not in payload["query"]
    assert ">" not in payload["query"]


def test_status_endpoint() -> None:
    client = TestClient(app)
    resp = client.get("/status/418")
    assert resp.status_code == 418
    assert "status=418" in resp.text
