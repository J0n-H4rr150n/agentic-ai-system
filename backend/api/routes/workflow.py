"""Workflow endpoints.

MVP: in-memory workflow storage.

A "workflow" is a saved GraphDefinition that can be loaded by id.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import threading
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.models.graph import GraphDefinition


router = APIRouter()


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


class WorkflowCreateRequest(BaseModel):
    graph: GraphDefinition


class WorkflowCreatedResponse(BaseModel):
    workflow_id: str


class WorkflowResponse(BaseModel):
    workflow_id: str
    created_at: datetime
    updated_at: datetime
    graph: GraphDefinition


@dataclass(slots=True)
class _WorkflowRecord:
    workflow_id: str
    created_at: datetime
    updated_at: datetime
    graph: GraphDefinition


_WORKFLOWS: dict[str, _WorkflowRecord] = {}
_WORKFLOWS_LOCK = threading.Lock()


@router.post("/api/workflow", response_model=WorkflowCreatedResponse)
async def create_workflow(request: WorkflowCreateRequest) -> WorkflowCreatedResponse:
    workflow_id = str(uuid4())
    now = _now_utc()

    record = _WorkflowRecord(workflow_id=workflow_id, created_at=now, updated_at=now, graph=request.graph)

    with _WORKFLOWS_LOCK:
        _WORKFLOWS[workflow_id] = record

    return WorkflowCreatedResponse(workflow_id=workflow_id)


@router.get("/api/workflow/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str) -> WorkflowResponse:
    with _WORKFLOWS_LOCK:
        record = _WORKFLOWS.get(workflow_id)

    if record is None:
        raise HTTPException(status_code=404, detail="workflow_id not found")

    return WorkflowResponse(
        workflow_id=record.workflow_id,
        created_at=record.created_at,
        updated_at=record.updated_at,
        graph=record.graph,
    )
