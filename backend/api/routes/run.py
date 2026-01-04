"""Run endpoints.

MVP: in-memory run storage and background execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import queue
import threading
import asyncio
from typing import Any, Literal
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.models.graph import GraphDefinition
from backend.models.run import StepTrace
from backend.nodes.builtin import NoopNode
from backend.runner.dependency import topological_sort
from backend.runner.executor import AsyncExecutor
from backend.runner.graph_parser import parse_graph
from backend.runner.state import StateContainer
from backend.runner.tracer import StepTracer


RunMode = Literal["run", "simulate", "test"]
RunStatus = Literal["running", "completed", "failed"]


class RunRequest(BaseModel):
    graph: GraphDefinition
    mode: RunMode = "run"


class RunCreatedResponse(BaseModel):
    run_id: str
    status: RunStatus


class RunStatusResponse(BaseModel):
    run_id: str
    status: RunStatus
    started_at: datetime
    completed_at: datetime | None
    trace: list[StepTrace]
    error: str | None = None


@dataclass(slots=True)
class _RunRecord:
    run_id: str
    status: RunStatus
    started_at: datetime
    completed_at: datetime | None = None
    trace: list[StepTrace] = field(default_factory=list)
    error: str | None = None
    events: queue.Queue[str | None] = field(default_factory=queue.Queue)


_RUNS: dict[str, _RunRecord] = {}
_RUNS_LOCK = threading.Lock()

router = APIRouter()


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


async def _execute_run(run_id: str, request: RunRequest) -> None:
    with _RUNS_LOCK:
        record = _RUNS[run_id]

    def _emit_step(step: StepTrace) -> None:
        record.events.put(_format_sse(event="step", data=step.model_dump()))

    tracer = StepTracer(on_record=_emit_step)

    try:
        plan = parse_graph(request.graph)
        # Detect cycles early with a clear error.
        topological_sort(plan)

        nodes = {node.id: NoopNode(node_id=node.id, node_type=node.type) for node in request.graph.nodes}
        executor = AsyncExecutor()
        await executor.run(plan, nodes, state=StateContainer(), tracer=tracer)

        with _RUNS_LOCK:
            rec = _RUNS[run_id]
            rec.status = "completed"
            rec.completed_at = _now_utc()
            rec.trace = tracer.steps()
            rec.error = None

        record.events.put(_format_sse(event="status", data={"run_id": run_id, "status": "completed"}))
        record.events.put(None)

    except Exception as exc:  # noqa: BLE001
        with _RUNS_LOCK:
            rec = _RUNS[run_id]
            rec.status = "failed"
            rec.completed_at = _now_utc()
            rec.trace = tracer.steps()
            rec.error = str(exc)

        record.events.put(
            _format_sse(event="status", data={"run_id": run_id, "status": "failed", "error": str(exc)})
        )
        record.events.put(None)


def _format_sse(*, event: str, data: dict[str, Any]) -> str:
    payload = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n"


@router.post("/api/run", response_model=RunCreatedResponse)
async def create_run(request: RunRequest, background_tasks: BackgroundTasks) -> RunCreatedResponse:
    run_id = str(uuid4())
    record = _RunRecord(run_id=run_id, status="running", started_at=_now_utc())

    with _RUNS_LOCK:
        _RUNS[run_id] = record

    background_tasks.add_task(_execute_run, run_id, request)
    return RunCreatedResponse(run_id=run_id, status="running")


@router.get("/api/run/{run_id}", response_model=RunStatusResponse)
async def get_run(run_id: str) -> RunStatusResponse:
    with _RUNS_LOCK:
        record = _RUNS.get(run_id)

    if record is None:
        raise HTTPException(status_code=404, detail="run_id not found")

    return RunStatusResponse(
        run_id=record.run_id,
        status=record.status,
        started_at=record.started_at,
        completed_at=record.completed_at,
        trace=record.trace,
        error=record.error,
    )


@router.get("/api/run/{run_id}/stream")
async def stream_run(run_id: str) -> StreamingResponse:
    with _RUNS_LOCK:
        record = _RUNS.get(run_id)

    if record is None:
        raise HTTPException(status_code=404, detail="run_id not found")

    async def _gen():
        # Send an initial non-terminal event so clients can confirm they are connected
        # without consuming the terminal status event out of order.
        yield _format_sse(event="hello", data={"run_id": run_id, "status": record.status})

        while True:
            chunk = await asyncio.to_thread(record.events.get)
            if chunk is None:
                break
            yield chunk

    return StreamingResponse(
        _gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )
