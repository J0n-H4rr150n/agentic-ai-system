"""Runner-scoped test doubles for execution modes.

These nodes are used when a run is started with mode="test".
They avoid external I/O while preserving basic output shapes.
"""

from __future__ import annotations

from typing import Any

from backend.nodes.base import BaseNode


class TestHTTPRequestNode(BaseNode):
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


class TestBrowserNode(BaseNode):
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
