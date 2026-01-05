"""Parallel Gate node.

Represents an explicit fork/join boundary in a workflow graph.

The current runner already executes independent branches concurrently. This node
is a lightweight, validated control primitive that can be used to make fork/join
structure explicit in the graph without changing runner semantics.

Config:
  gate: Optional string, one of: "fork", "join" (default: "join").
  fanout: Required when gate="fork"; int >= 2.
  output_key: Optional string output key (default: "parallel_gate_output").

Output:
  Writes `{output_key: {gate: ..., fanout: ...}}`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from backend.nodes.base import BaseNode


GateKind = Literal["fork", "join"]


@dataclass(frozen=True, slots=True)
class ParallelGateConfig:
    gate: GateKind
    fanout: int | None
    output_key: str


class ParallelGateNode(BaseNode):
    def __init__(self, node_id: str, *, config: dict[str, Any] | None = None) -> None:
        super().__init__(node_id=node_id, node_type="parallel_gate")
        self._config = dict(config or {})

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        cfg = _parse_config(self._config)

        payload: dict[str, Any] = {"gate": cfg.gate}
        if cfg.gate == "fork":
            payload["fanout"] = cfg.fanout

        return {cfg.output_key: payload}


NODE_TYPE = "parallel_gate"
NODE_CLASS = ParallelGateNode


def _parse_config(raw: dict[str, Any]) -> ParallelGateConfig:
    gate = raw.get("gate", "join")
    if gate not in {"fork", "join"}:
        raise ValueError("ParallelGateNode config.gate must be one of: fork, join")

    fanout = raw.get("fanout")
    if gate == "fork":
        if not isinstance(fanout, int) or isinstance(fanout, bool) or fanout < 2:
            raise ValueError("ParallelGateNode config.fanout must be an int >= 2 when gate=fork")
    else:
        # For join, ignore/clear fanout to keep output clean.
        fanout = None

    output_key = raw.get("output_key", "parallel_gate_output")
    if not isinstance(output_key, str) or not output_key:
        raise ValueError("ParallelGateNode config.output_key must be a non-empty string")

    return ParallelGateConfig(gate=gate, fanout=fanout, output_key=output_key)
