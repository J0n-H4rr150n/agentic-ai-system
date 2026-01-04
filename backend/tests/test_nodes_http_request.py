import asyncio

import httpx
import pytest

from backend.nodes.http.request import HTTPRequestNode


def _client_factory(transport: httpx.MockTransport) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=transport)


def test_http_request_node_get_captures_status_headers_body_text() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert str(request.url) == "https://example.test/"
        return httpx.Response(200, headers={"x-test": "1"}, text="ok")

    transport = httpx.MockTransport(handler)
    node = HTTPRequestNode(
        "h1",
        client_factory=lambda: _client_factory(transport),
        config={"method": "GET", "url": "https://example.test/"},
    )

    out = asyncio.run(node.execute({}))
    payload = out["http_output"]
    assert payload["status"] == 200
    assert payload["headers"]["x-test"] == "1"
    assert payload["body"] == "ok"


def test_http_request_node_post_json_sends_json_and_parses_json_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.headers["content-type"].startswith("application/json")
        assert request.read() == b"{\"hello\":\"world\"}"
        return httpx.Response(201, headers={"content-type": "application/json"}, json={"ok": True})

    transport = httpx.MockTransport(handler)
    node = HTTPRequestNode(
        "h1",
        client_factory=lambda: _client_factory(transport),
        config={"method": "POST", "url": "https://example.test/", "json_body": {"hello": "world"}},
    )

    out = asyncio.run(node.execute({}))
    assert out["http_output"]["status"] == 201
    assert out["http_output"]["body"] == {"ok": True}


def test_http_request_node_post_form_sends_data() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        body = request.read().decode("utf-8")
        # Form body order is not guaranteed.
        assert "a=1" in body
        assert "b=two" in body
        return httpx.Response(200, text="ok")

    transport = httpx.MockTransport(handler)
    node = HTTPRequestNode(
        "h1",
        client_factory=lambda: _client_factory(transport),
        config={"method": "POST", "url": "https://example.test/", "form_body": {"a": 1, "b": "two"}},
    )

    out = asyncio.run(node.execute({}))
    assert out["http_output"]["body"] == "ok"


def test_http_request_node_uses_url_key_and_headers_key() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert str(request.url) == "https://example.test/endpoint"
        assert request.headers["x-auth"] == "token"
        return httpx.Response(204, text="")

    transport = httpx.MockTransport(handler)
    node = HTTPRequestNode(
        "h1",
        client_factory=lambda: _client_factory(transport),
        config={"method": "GET", "url_key": "u", "headers_key": "h"},
    )

    out = asyncio.run(node.execute({"u": "https://example.test/endpoint", "h": {"x-auth": "token"}}))
    assert out["http_output"]["status"] == 204


def test_http_request_node_rejects_both_json_and_form_body() -> None:
    node = HTTPRequestNode(
        "h1",
        config={"method": "POST", "url": "https://example.test/", "json_body": {"a": 1}, "form_body": {"b": 2}},
    )

    with pytest.raises(ValueError, match="cannot send both"):
        asyncio.run(node.execute({}))
