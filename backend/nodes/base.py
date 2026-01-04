"""Base node execution interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseNode(ABC):
    """Abstract base for executable graph nodes."""

    def __init__(self, node_id: str, node_type: str) -> None:
        if not node_id or not isinstance(node_id, str):
            raise ValueError("node_id must be a non-empty string")
        if not node_type or not isinstance(node_type, str):
            raise ValueError("node_type must be a non-empty string")

        self.node_id = node_id
        self.node_type = node_type

    @abstractmethod
    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Execute this node.

        Args:
            state: Mutable state mapping for the current run.

        Returns:
            A dict payload representing the node output.
        """


class NodeExecutionError(RuntimeError):
    def __init__(self, node_id: str, message: str) -> None:
        super().__init__(f"Node {node_id}: {message}")
        self.node_id = node_id
