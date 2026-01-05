import asyncio
import httpx
import pytest

from backend.nodes.http.fuzzer import HTTPFuzzerNode


def test_http_fuzzer_expands_payloads_and_collects_responses() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        payload = request.url.params.get("q")
        return httpx.Response(200, json={"payload": payload})

    transport = httpx.MockTransport(handler)

    def client_factory() -> httpx.AsyncClient:
        return httpx.AsyncClient(transport=transport)

    node = HTTPFuzzerNode(
        "n1",
        client_factory=client_factory,
        config={
            "method": "GET",
            "url_template": "https://example.test/?q={payload}",
            "payloads": ["a", "b"],
        },
    )

    out = asyncio.run(node.execute({}))
    payload = out["http_fuzzer_output"]
    assert payload["summary"]["total"] == 2
    assert payload["summary"]["ok"] == 2
    bodies = [r["body"] for r in payload["results"]]
    assert bodies == [{"payload": "a"}, {"payload": "b"}]


def test_http_fuzzer_requires_payload_placeholder_in_template() -> None:
    node = HTTPFuzzerNode(
        "n1",
        config={
            "method": "GET",
            "url_template": "https://example.test/",  # missing {payload}
            "payloads": ["x"],
        },
    )

    with pytest.raises(ValueError, match="\\{payload\\}"):
        asyncio.run(node.execute({}))
