"""Run history endpoints.

Provides API access to persisted terminal run records.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.models.run import StepTrace
from backend.runs.store import RUN_HISTORY_STORE


router = APIRouter()


class RunHistoryListItem(BaseModel):
    run_id: str
    status: str
    started_at: datetime
    completed_at: datetime
    error: str | None = None


class RunHistoryListResponse(BaseModel):
    runs: list[RunHistoryListItem]


class RunHistoryDetailResponse(BaseModel):
    run_id: str
    status: str
    started_at: datetime
    completed_at: datetime
    trace: list[StepTrace]
    error: str | None = None


@router.get("/api/runs", response_model=RunHistoryListResponse)
async def list_runs(limit: int = Query(default=100, ge=1, le=500)) -> RunHistoryListResponse:
    records = RUN_HISTORY_STORE.list(limit=limit)
    return RunHistoryListResponse(
        runs=[
            RunHistoryListItem(
                run_id=r.run_id,
                status=r.status,
                started_at=r.started_at,
                completed_at=r.completed_at,
                error=r.error,
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
        status=record.status,
        started_at=record.started_at,
        completed_at=record.completed_at,
        trace=record.trace,
        error=record.error,
    )
