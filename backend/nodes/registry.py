"""Node registry.

The registry tracks which node types are supported by the backend.

This module intentionally keeps auto-discovery lightweight: node modules export
`NODE_TYPE` and `NODE_CLASS` so the registry can import and register them.
"""

from __future__ import annotations

from dataclasses import dataclass
import importlib
import pkgutil
from typing import Iterable

from backend.nodes.base import BaseNode


@dataclass(frozen=True, slots=True)
class NodeInfo:
    node_type: str
    import_path: str


class NodeRegistry:
    def __init__(self) -> None:
        self._nodes: dict[str, tuple[type[BaseNode], str]] = {}
        self._discovered = False

    def register(self, node_type: str, node_class: type[BaseNode], *, import_path: str) -> None:
        if not isinstance(node_type, str) or not node_type:
            raise ValueError("node_type must be a non-empty string")
        if not isinstance(import_path, str) or not import_path:
            raise ValueError("import_path must be a non-empty string")
        if not isinstance(node_class, type) or not issubclass(node_class, BaseNode):
            raise ValueError("node_class must be a BaseNode subclass")

        existing = self._nodes.get(node_type)
        if existing is not None and existing[0] is not node_class:
            raise ValueError(f"Duplicate node_type registration: {node_type}")

        self._nodes[node_type] = (node_class, import_path)

    def get(self, node_type: str) -> type[BaseNode]:
        if not isinstance(node_type, str) or not node_type:
            raise ValueError("node_type must be a non-empty string")

        record = self._nodes.get(node_type)
        if record is None:
            raise KeyError(node_type)
        return record[0]

    def list_all(self) -> list[NodeInfo]:
        return [
            NodeInfo(node_type=node_type, import_path=import_path)
            for node_type, (_, import_path) in sorted(self._nodes.items())
        ]

    def is_supported(self, node_type: str) -> bool:
        return node_type in self._nodes

    def discover(self, *, package: str = "backend.nodes") -> None:
        if self._discovered:
            return

        pkg = importlib.import_module(package)
        if not hasattr(pkg, "__path__"):
            raise ValueError(f"Package {package!r} is not a package")

        modules = _walk_modules(pkg.__path__, prefix=f"{package}.")
        for module_name in modules:
            module = importlib.import_module(module_name)
            node_type = getattr(module, "NODE_TYPE", None)
            node_class = getattr(module, "NODE_CLASS", None)
            if node_type is None or node_class is None:
                continue
            self.register(str(node_type), node_class, import_path=module_name)

        self._discovered = True


def _walk_modules(paths: Iterable[str], *, prefix: str) -> list[str]:
    out: list[str] = []
    for module_info in pkgutil.walk_packages(paths, prefix=prefix):
        if module_info.ispkg:
            continue
        out.append(module_info.name)
    return sorted(out)
