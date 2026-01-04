"""Built-in node implementations.

These are minimal nodes used to exercise the runner in early stories.
"""

from __future__ import annotations

from typing import Any

from backend.nodes.base import BaseNode


class NoopNode(BaseNode):
    """A node that performs no work and returns an empty output dict."""

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        return {}
