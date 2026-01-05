"""Runner-scoped test doubles for execution modes.

These nodes are used when a run is started with mode="test".
They avoid external I/O while preserving basic output shapes.
"""

from __future__ import annotations

from typing import Any

from backend.nodes.base import BaseNode


class StubHTTPRequestNode(BaseNode):
    """Deterministic HTTP node for test mode.

    Returns a minimal http_output payload without making a network request.
    """

    def __init__(self, node_id: str, *, config: dict[str, Any] | None = None) -> None:
        super().__init__(node_id=node_id, node_type="http_request")
        self._config = dict(config or {})

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        output_key = self._config.get("output_key", "http_output")
        if not isinstance(output_key, str) or not output_key:
            raise ValueError("HTTPRequestNode config.output_key must be a non-empty string")

        method = self._config.get("method", "GET")
        if not isinstance(method, str) or not method:
            raise ValueError("HTTPRequestNode config.method must be a non-empty string")

        url = self._config.get("url")
        if url is None:
            url_key = self._config.get("url_key")
            if isinstance(url_key, str) and url_key:
                url = state.get(url_key)
        if not isinstance(url, str) or not url.strip():
            url = "https://example.test/"

        return {
            output_key: {
                "mode": "test",
                "method": method,
                "url": url,
                "status": 200,
                "headers": {},
                "body": {"ok": True},
            }
        }


class StubBrowserNode(BaseNode):
    """Deterministic browser node for test mode.

    Does not navigate/click/type against a real page.
    """

    def __init__(self, node_id: str, *, config: dict[str, Any] | None = None) -> None:
        super().__init__(node_id=node_id, node_type="browser")
        self._config = dict(config or {})

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        output_key = self._config.get("output_key", "browser_output")
        if not isinstance(output_key, str) or not output_key:
            raise ValueError("BrowserNode config.output_key must be a non-empty string")

        action = self._config.get("action")
        if not isinstance(action, str) or not action:
            raise ValueError("BrowserNode config.action must be a non-empty string")

        return {
            output_key: {
                "mode": "test",
                "action": action,
                "ok": True,
                "details": {},
            }
        }


class StubHTTPFuzzerNode(BaseNode):
    """Deterministic HTTP fuzzer node for test mode.

    Returns a minimal http_fuzzer_output payload without making network requests.
    """

    def __init__(self, node_id: str, *, config: dict[str, Any] | None = None) -> None:
        super().__init__(node_id=node_id, node_type="http_fuzzer")
        self._config = dict(config or {})

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        output_key = self._config.get("output_key", "http_fuzzer_output")
        if not isinstance(output_key, str) or not output_key:
            raise ValueError("HTTPFuzzerNode config.output_key must be a non-empty string")

        url_template = self._config.get("url_template")
        if url_template is None:
            url_template_key = self._config.get("url_template_key")
            if isinstance(url_template_key, str) and url_template_key:
                url_template = state.get(url_template_key)
        if not isinstance(url_template, str) or not url_template:
            url_template = "https://example.test/?q={payload}"

        payloads = self._config.get("payloads")
        if payloads is None:
            payloads_key = self._config.get("payloads_key")
            if isinstance(payloads_key, str) and payloads_key:
                payloads = state.get(payloads_key)
        if not isinstance(payloads, list) or any(not isinstance(p, str) for p in payloads):
            payloads = ["test"]

        results = [
            {"payload": p, "ok": True, "status": 200, "headers": {}, "body": {"ok": True}}
            for p in payloads
        ]

        return {
            output_key: {
                "mode": "test",
                "method": self._config.get("method", "GET"),
                "url_template": url_template,
                "results": results,
                "summary": {"total": len(results), "ok": len(results), "error": 0},
            }
        }
