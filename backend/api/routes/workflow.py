"""Workflow endpoints.

MVP: in-memory workflow storage.

A "workflow" is a saved GraphDefinition that can be loaded by id.

In Phase 5 (F00006), workflows are versioned so a single workflow_id can
accumulate multiple saved graph versions.
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


class WorkflowVersionCreatedResponse(BaseModel):
    workflow_id: str
    version: int


class WorkflowResponse(BaseModel):
    workflow_id: str
    version: int
    created_at: datetime
    updated_at: datetime
    graph: GraphDefinition


class WorkflowVersionInfo(BaseModel):
    version: int
    created_at: datetime


class WorkflowVersionsResponse(BaseModel):
    workflow_id: str
    latest_version: int
    versions: list[WorkflowVersionInfo]


@dataclass(slots=True)
class _WorkflowVersion:
    version: int
    created_at: datetime
    graph: GraphDefinition


@dataclass(slots=True)
class _WorkflowRecord:
    workflow_id: str
    created_at: datetime
    updated_at: datetime
    versions: list[_WorkflowVersion]


_WORKFLOWS: dict[str, _WorkflowRecord] = {}
_WORKFLOWS_LOCK = threading.Lock()


@router.post("/api/workflow", response_model=WorkflowCreatedResponse)
async def create_workflow(request: WorkflowCreateRequest) -> WorkflowCreatedResponse:
    workflow_id = str(uuid4())
    now = _now_utc()

    record = _WorkflowRecord(
        workflow_id=workflow_id,
        created_at=now,
        updated_at=now,
        versions=[_WorkflowVersion(version=1, created_at=now, graph=request.graph)],
    )

    with _WORKFLOWS_LOCK:
        _WORKFLOWS[workflow_id] = record

    return WorkflowCreatedResponse(workflow_id=workflow_id)


@router.post("/api/workflow/{workflow_id}/version", response_model=WorkflowVersionCreatedResponse)
async def create_workflow_version(workflow_id: str, request: WorkflowCreateRequest) -> WorkflowVersionCreatedResponse:
    now = _now_utc()

    with _WORKFLOWS_LOCK:
        record = _WORKFLOWS.get(workflow_id)
        if record is None:
            raise HTTPException(status_code=404, detail="workflow_id not found")

        next_version = (record.versions[-1].version + 1) if record.versions else 1
        record.versions.append(_WorkflowVersion(version=next_version, created_at=now, graph=request.graph))
        record.updated_at = now

    return WorkflowVersionCreatedResponse(workflow_id=workflow_id, version=next_version)


@router.get("/api/workflow/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str, version: int | None = None) -> WorkflowResponse:
    with _WORKFLOWS_LOCK:
        record = _WORKFLOWS.get(workflow_id)

    if record is None:
        raise HTTPException(status_code=404, detail="workflow_id not found")

    if not record.versions:
        raise HTTPException(status_code=500, detail="workflow has no versions")

    selected: _WorkflowVersion | None
    if version is None:
        selected = record.versions[-1]
    else:
        selected = next((v for v in record.versions if v.version == version), None)
        if selected is None:
            raise HTTPException(status_code=404, detail="workflow version not found")

    return WorkflowResponse(
        workflow_id=record.workflow_id,
        version=selected.version,
        created_at=record.created_at,
        updated_at=record.updated_at,
        graph=selected.graph,
    )


@router.get("/api/workflow/{workflow_id}/versions", response_model=WorkflowVersionsResponse)
async def list_workflow_versions(workflow_id: str) -> WorkflowVersionsResponse:
    with _WORKFLOWS_LOCK:
        record = _WORKFLOWS.get(workflow_id)

    if record is None:
        raise HTTPException(status_code=404, detail="workflow_id not found")

    versions = [WorkflowVersionInfo(version=v.version, created_at=v.created_at) for v in record.versions]
    latest_version = record.versions[-1].version if record.versions else 0
    return WorkflowVersionsResponse(workflow_id=workflow_id, latest_version=latest_version, versions=versions)
