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

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.models.graph import GraphDefinition
from backend.models.run import RunCheckpoint, StepTrace
from backend.runner.dependency import topological_sort
from backend.runner.executor import AsyncExecutor, RunPaused
from backend.runner.graph_parser import parse_graph
from backend.runner.node_factory import build_nodes_for_graph
from backend.runner.state import StateContainer
from backend.runner.tracer import StepTracer


RunMode = Literal["run", "simulate", "test"]
RunStatus = Literal["running", "paused", "completed", "failed"]


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
    paused_at: datetime | None = None
    completed_at: datetime | None
    trace: list[StepTrace]
    error: str | None = None


@dataclass(slots=True)
class _RunRecord:
    run_id: str
    status: RunStatus
    started_at: datetime
    paused_at: datetime | None = None
    completed_at: datetime | None = None
    trace: list[StepTrace] = field(default_factory=list)
    error: str | None = None
    events: queue.Queue[str | None] = field(default_factory=queue.Queue)
    pause_requested: bool = False
    checkpoint: RunCheckpoint | None = None


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

    def _should_pause() -> bool:
        with _RUNS_LOCK:
            rec = _RUNS.get(run_id)
            return bool(rec is not None and rec.pause_requested)

    try:
        plan = parse_graph(request.graph)
        # Detect cycles early with a clear error.
        topological_sort(plan)

        nodes = build_nodes_for_graph(run_id=run_id, graph_nodes=request.graph.nodes)
        executor = AsyncExecutor()
        await executor.run(plan, nodes, state=StateContainer(), tracer=tracer, should_pause=_should_pause)

        with _RUNS_LOCK:
            rec = _RUNS[run_id]
            rec.status = "completed"
            rec.paused_at = None
            rec.completed_at = _now_utc()
            rec.trace = tracer.steps()
            rec.error = None

        record.events.put(_format_sse(event="status", data={"run_id": run_id, "status": "completed"}))
        record.events.put(None)

    except RunPaused as paused:
        checkpoint = RunCheckpoint(
            run_id=run_id,
            created_at=_now_utc(),
            state=paused.checkpoint.state,
            completed_node_ids=list(paused.checkpoint.completed_node_ids),
            ready_node_ids=list(paused.checkpoint.ready_node_ids),
            indegree=dict(paused.checkpoint.indegree),
        )

        with _RUNS_LOCK:
            rec = _RUNS[run_id]
            rec.status = "paused"
            rec.paused_at = _now_utc()
            rec.completed_at = None
            rec.trace = tracer.steps()
            rec.error = None
            rec.checkpoint = checkpoint

        record.events.put(_format_sse(event="status", data={"run_id": run_id, "status": "paused"}))
        record.events.put(None)

    except Exception as exc:  # noqa: BLE001
        with _RUNS_LOCK:
            rec = _RUNS[run_id]
            rec.status = "failed"
            rec.paused_at = None
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
async def create_run(request: RunRequest) -> RunCreatedResponse:
    run_id = str(uuid4())
    record = _RunRecord(run_id=run_id, status="running", started_at=_now_utc())

    with _RUNS_LOCK:
        _RUNS[run_id] = record

    # Run concurrently so control endpoints (pause/stop) can act while the run is in-flight.
    # We use a dedicated daemon thread so execution isn't tied to the request event loop
    # (which may be short-lived under TestClient).
    def _runner() -> None:
        asyncio.run(_execute_run(run_id, request))

    threading.Thread(target=_runner, name=f"run-{run_id}", daemon=True).start()
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
        paused_at=record.paused_at,
        completed_at=record.completed_at,
        trace=record.trace,
        error=record.error,
    )


class RunControlResponse(BaseModel):
    run_id: str
    status: RunStatus


@router.post("/api/run/{run_id}/pause", response_model=RunControlResponse)
async def pause_run(run_id: str) -> RunControlResponse:
    with _RUNS_LOCK:
        record = _RUNS.get(run_id)

        if record is None:
            raise HTTPException(status_code=404, detail="run_id not found")

        # Idempotent: pausing a paused/completed/failed run does nothing.
        if record.status == "running":
            record.pause_requested = True

        return RunControlResponse(run_id=record.run_id, status=record.status)


@router.get("/api/run/{run_id}/checkpoint", response_model=RunCheckpoint)
async def get_checkpoint(run_id: str) -> RunCheckpoint:
    with _RUNS_LOCK:
        record = _RUNS.get(run_id)

    if record is None:
        raise HTTPException(status_code=404, detail="run_id not found")
    if record.checkpoint is None:
        raise HTTPException(status_code=404, detail="checkpoint not found")

    return record.checkpoint


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
