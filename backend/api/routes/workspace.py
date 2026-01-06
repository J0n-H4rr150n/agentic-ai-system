"""Workspace endpoints.

A "workspace" is a UI-level document that can be saved/loaded and versioned.

Storage:
- In-memory by default (tests/local)
- Postgres-backed when DATABASE_URL is set
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.workspaces.store import WORKSPACE_STORE


router = APIRouter()


class WorkspaceCreateRequest(BaseModel):
    state: dict = Field(default_factory=dict)
    name: str | None = None


class WorkspaceCreatedResponse(BaseModel):
    workspace_id: str


class WorkspaceVersionCreatedResponse(BaseModel):
    workspace_id: str
    version: int


class WorkspaceResponse(BaseModel):
    workspace_id: str
    name: str | None
    version: int
    created_at: datetime
    updated_at: datetime
    state: dict


class WorkspaceVersionInfo(BaseModel):
    version: int
    created_at: datetime


class WorkspaceVersionsResponse(BaseModel):
    workspace_id: str
    latest_version: int
    versions: list[WorkspaceVersionInfo]


class WorkspaceListItem(BaseModel):
    workspace_id: str
    name: str | None
    latest_version: int
    created_at: datetime
    updated_at: datetime


class WorkspaceListResponse(BaseModel):
    workspaces: list[WorkspaceListItem]


@router.post("/api/workspace", response_model=WorkspaceCreatedResponse)
async def create_workspace(request: WorkspaceCreateRequest) -> WorkspaceCreatedResponse:
    workspace_id = WORKSPACE_STORE.create(state=request.state, name=request.name)
    return WorkspaceCreatedResponse(workspace_id=workspace_id)


@router.get("/api/workspace", response_model=WorkspaceListResponse)
async def list_workspaces() -> WorkspaceListResponse:
    records = WORKSPACE_STORE.list()
    items: list[WorkspaceListItem] = []

    for r in records:
        latest_version = r.versions[-1].version if r.versions else 0
        items.append(
            WorkspaceListItem(
                workspace_id=r.workspace_id,
                name=r.name,
                latest_version=latest_version,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
        )

    return WorkspaceListResponse(workspaces=items)


@router.post("/api/workspace/{workspace_id}/version", response_model=WorkspaceVersionCreatedResponse)
async def create_workspace_version(
    workspace_id: str, request: WorkspaceCreateRequest
) -> WorkspaceVersionCreatedResponse:
    try:
        next_version = WORKSPACE_STORE.create_version(workspace_id, state=request.state, name=request.name)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="workspace_id not found") from exc

    return WorkspaceVersionCreatedResponse(workspace_id=workspace_id, version=next_version)


@router.get("/api/workspace/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(workspace_id: str, version: int | None = None) -> WorkspaceResponse:
    try:
        record, selected = WORKSPACE_STORE.get(workspace_id, version=version)
    except KeyError as exc:
        if exc.args and isinstance(exc.args[0], str) and ":" in exc.args[0]:
            raise HTTPException(status_code=404, detail="workspace version not found") from exc
        raise HTTPException(status_code=404, detail="workspace_id not found") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return WorkspaceResponse(
        workspace_id=record.workspace_id,
        name=record.name,
        version=selected.version,
        created_at=record.created_at,
        updated_at=record.updated_at,
        state=selected.state,
    )


@router.get("/api/workspace/{workspace_id}/versions", response_model=WorkspaceVersionsResponse)
async def list_workspace_versions(workspace_id: str) -> WorkspaceVersionsResponse:
    try:
        latest_version, versions_raw = WORKSPACE_STORE.list_versions(workspace_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="workspace_id not found") from exc

    versions = [WorkspaceVersionInfo(version=v.version, created_at=v.created_at) for v in versions_raw]
    return WorkspaceVersionsResponse(workspace_id=workspace_id, latest_version=latest_version, versions=versions)
