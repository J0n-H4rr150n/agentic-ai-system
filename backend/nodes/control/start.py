"""Start node.

Initializes run state.

The current runner interface passes only a mutable state mapping to node execution.
To keep this node useful before config/context is fully wired through the runner,
StartNode accepts an initialization config at construction time.

Config:
    initial_state: Optional mapping merged into state at the start of the run.
        - Only dict values are accepted.

Output:
    Returns the `initial_state` mapping (or {}), so the executor will merge it into
    the run state.
"""

from __future__ import annotations

from typing import Any

from backend.nodes.base import BaseNode


class StartNode(BaseNode):
    """Start node that injects an initial state mapping."""

    def __init__(self, node_id: str, config: dict[str, Any] | None = None) -> None:
        super().__init__(node_id=node_id, node_type="start")
        self._config = dict(config or {})

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        initial_state = self._config.get("initial_state")
        if initial_state is None:
            return {}

        if not isinstance(initial_state, dict):
            raise ValueError("StartNode config.initial_state must be a dict")

        return dict(initial_state)


NODE_TYPE = "start"
NODE_CLASS = StartNode
