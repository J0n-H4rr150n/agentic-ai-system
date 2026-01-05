"""Graph validation endpoint.

Validate mode checks graph structure/dependencies/type compatibility without executing.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.models.graph import GraphDefinition
from backend.runner.dependency import topological_sort
from backend.runner.graph_parser import parse_graph


router = APIRouter()


class ValidateRequest(BaseModel):
    graph: GraphDefinition


class ValidateResponse(BaseModel):
    ok: bool
    details: dict[str, Any] = {}


@router.post("/api/validate", response_model=ValidateResponse)
async def validate_graph(request: ValidateRequest) -> ValidateResponse:
    try:
        plan = parse_graph(request.graph)
        topological_sort(plan)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ValidateResponse(ok=True, details={"node_count": len(request.graph.nodes or []), "edge_count": len(request.graph.edges or [])})
