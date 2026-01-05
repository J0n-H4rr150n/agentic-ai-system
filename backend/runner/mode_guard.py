"""Execution-mode guards.

Simulate mode is intended to be a dry-run with no side effects.
We enforce conservative restrictions by node type.
"""

from __future__ import annotations

from typing import Any, Callable

from backend.nodes.base import BaseNode


Validator = Callable[[dict[str, Any]], None]


class GuardedNode(BaseNode):
    """Wrap a node with an execution-time validator."""

    def __init__(self, *, inner: BaseNode, validate: Validator) -> None:
        super().__init__(node_id=inner.node_id, node_type=inner.node_type)
        self._inner = inner
        self._validate = validate

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        self._validate(state)
        return await self._inner.execute(state)


def simulate_http_validate(config: dict[str, Any]) -> Validator:
    """Allow only safe HTTP methods in simulate mode."""

    def _validate(_: dict[str, Any]) -> None:
        method = config.get("method")
        if method not in {"GET", "HEAD", "OPTIONS"}:
            raise ValueError(
                "simulate mode only allows HTTP methods: GET, HEAD, OPTIONS "
                "(set request.mode=run to allow POST/PUT/PATCH/DELETE)"
            )

    return _validate


def simulate_browser_validate(config: dict[str, Any]) -> Validator:
    """Allow only navigation in simulate mode.

    This blocks click/type actions, which can trigger stateful writes.
    """

    def _validate(_: dict[str, Any]) -> None:
        action = config.get("action")
        if action != "navigate":
            raise ValueError(
                "simulate mode only allows browser action 'navigate' "
                "(set request.mode=run to allow click/type)"
            )

    return _validate
