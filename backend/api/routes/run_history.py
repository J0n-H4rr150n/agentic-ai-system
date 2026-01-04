"""Run history endpoints.

Provides API access to persisted terminal run records.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.models.run import RunCheckpoint, StepTrace
from backend.runs.store import RUN_HISTORY_STORE, TerminalRunStatus


router = APIRouter()


class RunHistoryListItem(BaseModel):
    run_id: str
    workflow_id: str | None = None
    status: str
    started_at: datetime
    completed_at: datetime
    error: str | None = None
    has_checkpoint: bool = False


class RunHistoryListResponse(BaseModel):
    runs: list[RunHistoryListItem]


class RunHistoryDetailResponse(BaseModel):
    run_id: str
    workflow_id: str | None = None
    status: str
    started_at: datetime
    completed_at: datetime
    trace: list[StepTrace]
    error: str | None = None
    checkpoint: RunCheckpoint | None = None


@router.get("/api/runs", response_model=RunHistoryListResponse)
async def list_runs(
    workflow_id: str | None = Query(default=None, min_length=1),
    status: TerminalRunStatus | None = Query(default=None),
    node_type: str | None = Query(default=None, min_length=1),
    limit: int = Query(default=100, ge=1, le=500),
) -> RunHistoryListResponse:
    records = RUN_HISTORY_STORE.list(workflow_id=workflow_id, status=status, node_type=node_type, limit=limit)
    return RunHistoryListResponse(
        runs=[
            RunHistoryListItem(
                run_id=r.run_id,
                workflow_id=r.workflow_id,
                status=r.status,
                started_at=r.started_at,
                completed_at=r.completed_at,
                error=r.error,
                has_checkpoint=r.checkpoint is not None,
            )
            for r in records
        ]
    )


@router.get("/api/runs/{run_id}", response_model=RunHistoryDetailResponse)
async def get_run_history(run_id: str) -> RunHistoryDetailResponse:
    record = RUN_HISTORY_STORE.get(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail="run_id not found")

    return RunHistoryDetailResponse(
        run_id=record.run_id,
        workflow_id=record.workflow_id,
        status=record.status,
        started_at=record.started_at,
        completed_at=record.completed_at,
        trace=record.trace,
        error=record.error,
        checkpoint=record.checkpoint,
    )
