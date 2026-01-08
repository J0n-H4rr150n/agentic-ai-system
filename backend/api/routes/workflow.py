"""Workflow endpoints.

MVP: in-memory workflow storage.

A "workflow" is a saved GraphDefinition that can be loaded by id.

In Phase 5 (F00006), workflows are versioned so a single workflow_id can
accumulate multiple saved graph versions.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.models.graph import GraphDefinition
from backend.workflows.schema import infer_workflow_io_schema
from backend.workflows.store import WORKFLOW_STORE


router = APIRouter()


class WorkflowCreateRequest(BaseModel):
    graph: GraphDefinition
    name: str | None = None


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


class WorkflowListItem(BaseModel):
    workflow_id: str
    name: str | None
    latest_version: int
    created_at: datetime
    updated_at: datetime


class WorkflowListResponse(BaseModel):
    workflows: list[WorkflowListItem]


class WorkflowSchemaResponse(BaseModel):
    workflow_id: str
    version: int
    inputs: list[str]
    outputs: list[str]
    warnings: list[str]


@router.post("/api/workflow", response_model=WorkflowCreatedResponse)
async def create_workflow(request: WorkflowCreateRequest) -> WorkflowCreatedResponse:
    workflow_id = WORKFLOW_STORE.create(request.graph, name=request.name)
    return WorkflowCreatedResponse(workflow_id=workflow_id)


@router.get("/api/workflow", response_model=WorkflowListResponse)
async def list_workflows() -> WorkflowListResponse:
    records = WORKFLOW_STORE.list()
    workflows = [
        WorkflowListItem(
            workflow_id=r.workflow_id,
            name=r.name,
            latest_version=r.versions[-1].version if r.versions else 0,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in records
    ]

    return WorkflowListResponse(workflows=workflows)


@router.post("/api/workflow/{workflow_id}/version", response_model=WorkflowVersionCreatedResponse)
async def create_workflow_version(workflow_id: str, request: WorkflowCreateRequest) -> WorkflowVersionCreatedResponse:
    try:
        next_version = WORKFLOW_STORE.create_version(workflow_id, request.graph)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="workflow_id not found") from exc

    return WorkflowVersionCreatedResponse(workflow_id=workflow_id, version=next_version)


@router.get("/api/workflow/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str, version: int | None = None) -> WorkflowResponse:
    try:
        record, selected = WORKFLOW_STORE.get(workflow_id, version=version)
    except KeyError as exc:
        # Differentiate unknown workflow id vs unknown version.
        if exc.args and isinstance(exc.args[0], str) and ":" in exc.args[0]:
            raise HTTPException(status_code=404, detail="workflow version not found") from exc
        raise HTTPException(status_code=404, detail="workflow_id not found") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return WorkflowResponse(
        workflow_id=record.workflow_id,
        version=selected.version,
        created_at=record.created_at,
        updated_at=record.updated_at,
        graph=selected.graph,
    )


@router.get("/api/workflow/{workflow_id}/versions", response_model=WorkflowVersionsResponse)
async def list_workflow_versions(workflow_id: str) -> WorkflowVersionsResponse:
    try:
        latest_version, versions_raw = WORKFLOW_STORE.list_versions(workflow_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="workflow_id not found") from exc

    versions = [WorkflowVersionInfo(version=v.version, created_at=v.created_at) for v in versions_raw]
    return WorkflowVersionsResponse(workflow_id=workflow_id, latest_version=latest_version, versions=versions)


@router.get("/api/workflow/{workflow_id}/schema", response_model=WorkflowSchemaResponse)
async def get_workflow_schema(workflow_id: str, version: int | None = None) -> WorkflowSchemaResponse:
    try:
        _, selected = WORKFLOW_STORE.get(workflow_id, version=version)
    except KeyError as exc:
        if exc.args and isinstance(exc.args[0], str) and ":" in exc.args[0]:
            raise HTTPException(status_code=404, detail="workflow version not found") from exc
        raise HTTPException(status_code=404, detail="workflow_id not found") from exc

    inferred = infer_workflow_io_schema(selected.graph, store=WORKFLOW_STORE)

    return WorkflowSchemaResponse(
        workflow_id=workflow_id,
        version=selected.version,
        inputs=sorted(inferred.inputs),
        outputs=sorted(inferred.outputs),
        warnings=list(inferred.warnings),
    )
