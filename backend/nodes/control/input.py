"""Input node.

Stores a configured value into state under a configurable output key.

This is intentionally simple: it enables workflows to define multiple independent
inputs (URL, prompts, system instructions, etc.) without hard-coding Start node
fields.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.nodes.base import BaseNode


@dataclass(frozen=True, slots=True)
class InputNodeConfig:
    label: str | None = None
    value: str = ""
    output_key: str = "input_value"


class InputNode(BaseNode):
    """Control node that writes a configured value into state."""

    def __init__(self, node_id: str, *, config: dict[str, Any] | None = None) -> None:
        super().__init__(node_id=node_id, node_type="input")
        self._config = dict(config or {})

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        cfg = _parse_config(self._config)
        return {cfg.output_key: cfg.value}


NODE_TYPE = "input"
NODE_CLASS = InputNode


def _parse_config(raw: dict[str, Any]) -> InputNodeConfig:
    label = raw.get("label")
    if label is not None and (not isinstance(label, str) or not label.strip()):
        raise ValueError("InputNode config.label must be a non-empty string when provided")

    value = raw.get("value", "")
    if value is None:
        value = ""
    if not isinstance(value, str):
        raise ValueError("InputNode config.value must be a string")

    output_key = raw.get("output_key", "input_value")
    if not isinstance(output_key, str) or not output_key:
        raise ValueError("InputNode config.output_key must be a non-empty string")

    return InputNodeConfig(label=label, value=value, output_key=output_key)
