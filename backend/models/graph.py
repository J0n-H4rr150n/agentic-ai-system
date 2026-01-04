"""Graph schema models.

These models define the JSON contract between the frontend canvas and the backend runner.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class Point(BaseModel):
    """A 2D point in world coordinates."""

    x: float
    y: float

    @field_validator("x", "y")
    @classmethod
    def _finite(cls, value: float) -> float:
        if not isinstance(value, (int, float)):
            raise TypeError("Coordinate must be a number")
        if value != value or value in (float("inf"), float("-inf")):
            raise ValueError("Coordinate must be finite")
        return float(value)


class Size(BaseModel):
    """A width/height pair in world units."""

    width: float = Field(gt=0)
    height: float = Field(gt=0)


PortKind = Literal["input", "output"]


class PortDefinition(BaseModel):
    """A node port exposed for wiring."""

    id: str = Field(min_length=1)
    kind: PortKind
    label: str | None = None


class InterruptConfig(BaseModel):
    """Human-in-the-loop interrupt configuration for a node.

    This is configuration-only in early stories; executor pause/resume behavior
    is implemented separately.
    """

    before: bool = False
    after: bool = False
    reason: str | None = Field(default=None, max_length=280)

    @model_validator(mode="after")
    def _validate_flags(self) -> "InterruptConfig":
        if not (self.before or self.after):
            raise ValueError("InterruptConfig must set before and/or after")
        return self


class NodeDefinition(BaseModel):
    """A node instance on the canvas."""

    id: str = Field(min_length=1)
    type: str = Field(min_length=1)
    title: str | None = None

    position: Point
    size: Size

    ports: list[PortDefinition] = Field(default_factory=list)
    config: dict[str, Any] = Field(default_factory=dict)
    interrupt: InterruptConfig | None = None

    @model_validator(mode="after")
    def _normalize(self) -> "NodeDefinition":
        if self.title is None:
            self.title = self.type
        return self


class EdgeEndpoint(BaseModel):
    nodeId: str = Field(min_length=1)
    portId: str = Field(min_length=1)


class EdgeDefinition(BaseModel):
    """A directed edge connecting an output port to an input port."""

    id: str = Field(min_length=1)
    from_: EdgeEndpoint = Field(alias="from")
    to: EdgeEndpoint


class GraphDefinition(BaseModel):
    """A complete graph definition exported from the canvas."""

    version: int = 1
    nodes: list[NodeDefinition]
    edges: list[EdgeDefinition]

    @model_validator(mode="after")
    def _validate_integrity(self) -> "GraphDefinition":
        node_ids = [n.id for n in self.nodes]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("Node ids must be unique")

        edge_ids = [e.id for e in self.edges]
        if len(edge_ids) != len(set(edge_ids)):
            raise ValueError("Edge ids must be unique")

        node_by_id = {n.id: n for n in self.nodes}
        for edge in self.edges:
            if edge.from_.nodeId not in node_by_id:
                raise ValueError(f"Edge {edge.id} references missing from.nodeId")
            if edge.to.nodeId not in node_by_id:
                raise ValueError(f"Edge {edge.id} references missing to.nodeId")

            from_node = node_by_id[edge.from_.nodeId]
            to_node = node_by_id[edge.to.nodeId]

            from_port_ids = {p.id for p in from_node.ports}
            to_port_ids = {p.id for p in to_node.ports}

            if from_port_ids and edge.from_.portId not in from_port_ids:
                raise ValueError(f"Edge {edge.id} references missing from.portId")
            if to_port_ids and edge.to.portId not in to_port_ids:
                raise ValueError(f"Edge {edge.id} references missing to.portId")

        return self
