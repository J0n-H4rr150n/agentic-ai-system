"""HTTP-backed page-like implementation for browser nodes.

This provides a minimal `BrowserPageLike` surface (`goto/click/fill`) and
observation methods (`content/screenshot`) without requiring Playwright.

Used for MVP end-to-end tests against a local HTTP server.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
from typing import Any

import httpx


# 1x1 transparent PNG
_TINY_PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO2Z3GgAAAAASUVORK5CYII="
)
_TINY_PNG_BYTES = base64.b64decode(_TINY_PNG_BASE64)


@dataclass(slots=True)
class HttpxPage:
    """A minimal page-like object backed by httpx."""

    timeout_seconds: float = 10.0
    last_url: str | None = None
    _html: str = ""
    network_log: list[dict[str, Any]] = field(default_factory=list)

    def goto(self, url: str) -> None:
        if not isinstance(url, str) or not url.strip():
            raise ValueError("url must be a non-empty string")

        with httpx.Client(timeout=self.timeout_seconds, follow_redirects=True) as client:
            resp = client.get(url)

        self.last_url = str(resp.request.url)
        self._html = resp.text
        self.network_log.append({"method": "GET", "url": self.last_url, "status": int(resp.status_code)})

    def click(self, selector: str) -> None:
        # Not supported by this lightweight implementation.
        return

    def fill(self, selector: str, text: str) -> None:
        # Not supported by this lightweight implementation.
        return

    def content(self) -> str:
        return self._html

    def screenshot(self) -> bytes:
        return _TINY_PNG_BYTES

    def screenshot_som(self) -> bytes:
        return _TINY_PNG_BYTES
