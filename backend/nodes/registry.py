"""Node registry.

MVP: a minimal registry used by the graph parser to validate node types.
"""

from __future__ import annotations


class NodeRegistry:
    def __init__(self, allowed_types: set[str] | None = None) -> None:
        self._allowed_types = allowed_types or {
            "start",
            "end",
            "router",
            "browser",
            "llm",
            "http",
        }

    def is_supported(self, node_type: str) -> bool:
        return node_type in self._allowed_types
