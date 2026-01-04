"""Mock node implementation for unit tests and early runner development."""

from __future__ import annotations

from typing import Any

from backend.nodes.base import BaseNode


class MockNode(BaseNode):
    def __init__(self, node_id: str, node_type: str = "mock", output: dict[str, Any] | None = None) -> None:
        super().__init__(node_id=node_id, node_type=node_type)
        self.output = output or {"ok": True}
        self.calls: list[dict[str, Any]] = []

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        self.calls.append({"state": dict(state)})
        return dict(self.output)
