"""End node.

Finalizes a run by producing a final result snapshot.

Config:
    result_key: The state key to store the final snapshot under (default: "result").
    include_keys: Optional list of state keys to include in the snapshot.

Output:
    {result_key: snapshot}

Notes:
    The snapshot is taken from the state as provided to execute(). To avoid
    self-referential output, the snapshot excludes the result_key itself.
"""

from __future__ import annotations

from typing import Any

from backend.nodes.base import BaseNode


class EndNode(BaseNode):
    """End node that returns a final state snapshot under a result key."""

    def __init__(self, node_id: str, config: dict[str, Any] | None = None) -> None:
        super().__init__(node_id=node_id, node_type="end")
        self._config = dict(config or {})

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        result_key = self._config.get("result_key", "result")
        if not isinstance(result_key, str) or not result_key:
            raise ValueError("EndNode config.result_key must be a non-empty string")

        snapshot = dict(state)
        snapshot.pop(result_key, None)

        include_keys = self._config.get("include_keys")
        if include_keys is not None:
            if not isinstance(include_keys, list) or not all(isinstance(k, str) for k in include_keys):
                raise ValueError("EndNode config.include_keys must be a list of strings")
            snapshot = {k: snapshot.get(k) for k in include_keys if k in snapshot}

        return {result_key: snapshot}


NODE_TYPE = "end"
NODE_CLASS = EndNode
