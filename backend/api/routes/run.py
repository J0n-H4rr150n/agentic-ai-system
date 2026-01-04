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

from fastapi import APIRouter, HTTPException, WebSocket
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from starlette.websockets import WebSocketDisconnect

from backend.models.graph import GraphDefinition
from backend.models.run import RunCheckpoint, StepTrace
from backend.runner.dependency import topological_sort
from backend.runner.executor import AsyncExecutor, ExecutionCheckpoint, RunCancelled, RunInterrupted, RunPaused
from backend.runner.graph_parser import parse_graph
from backend.runner.node_factory import build_nodes_for_graph
from backend.runner.state import StateContainer
from backend.runner.tracer import StepTracer
from backend.runs.store import RUN_HISTORY_STORE


RunMode = Literal["run", "simulate", "test"]
RunStatus = Literal["running", "paused", "completed", "failed", "cancelled"]
PauseReason = Literal["manual", "interrupt"]


class PendingInterrupt(BaseModel):
    node_id: str
    phase: Literal["before", "after"]
    reason: str | None = None


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
    pause_reason: PauseReason | None = None
    pending_interrupt: PendingInterrupt | None = None


@dataclass(slots=True)
class _RunRecord:
    run_id: str
    status: RunStatus
    started_at: datetime
    request: RunRequest
    paused_at: datetime | None = None
    completed_at: datetime | None = None
    trace: list[StepTrace] = field(default_factory=list)
    error: str | None = None
    pause_reason: PauseReason | None = None
    pending_interrupt: PendingInterrupt | None = None
    events: queue.Queue[str | None] = field(default_factory=queue.Queue)
    pause_requested: bool = False
    cancel_requested: bool = False
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

    def _should_cancel() -> bool:
        with _RUNS_LOCK:
            rec = _RUNS.get(run_id)
            return bool(rec is not None and rec.cancel_requested)

    try:
        plan = parse_graph(request.graph)
        # Detect cycles early with a clear error.
        topological_sort(plan)

        nodes = build_nodes_for_graph(run_id=run_id, graph_nodes=request.graph.nodes)
        executor = AsyncExecutor()
        await executor.run(
            plan,
            nodes,
            state=StateContainer(),
            tracer=tracer,
            should_pause=_should_pause,
            should_cancel=_should_cancel,
        )

        with _RUNS_LOCK:
            rec = _RUNS[run_id]
            rec.status = "completed"
            rec.paused_at = None
            rec.completed_at = _now_utc()
            rec.trace = tracer.steps()
            rec.error = None
            rec.pause_reason = None
            rec.pending_interrupt = None
            rec.checkpoint = None

            RUN_HISTORY_STORE.persist_terminal(
                run_id=rec.run_id,
                status="completed",
                started_at=rec.started_at,
                completed_at=rec.completed_at,
                trace=rec.trace,
                error=rec.error,
            )

        record.events.put(_format_sse(event="status", data={"run_id": run_id, "status": "completed"}))
        record.events.put(None)

    except RunCancelled:
        with _RUNS_LOCK:
            rec = _RUNS[run_id]
            rec.status = "cancelled"
            rec.pause_requested = False
            rec.cancel_requested = False
            rec.paused_at = None
            rec.completed_at = _now_utc()
            rec.trace = tracer.steps()
            rec.error = None
            rec.checkpoint = None
            rec.pause_reason = None
            rec.pending_interrupt = None

            RUN_HISTORY_STORE.persist_terminal(
                run_id=rec.run_id,
                status="cancelled",
                started_at=rec.started_at,
                completed_at=rec.completed_at,
                trace=rec.trace,
                error=rec.error,
            )

        record.events.put(_format_sse(event="status", data={"run_id": run_id, "status": "cancelled"}))
        record.events.put(None)

    except RunInterrupted as interrupted:
        checkpoint = RunCheckpoint(
            run_id=run_id,
            created_at=_now_utc(),
            state=interrupted.checkpoint.state,
            completed_node_ids=list(interrupted.checkpoint.completed_node_ids),
            ready_node_ids=list(interrupted.checkpoint.ready_node_ids),
            indegree=dict(interrupted.checkpoint.indegree),
            handled_interrupts=list(interrupted.checkpoint.handled_interrupts),
        )

        pending = PendingInterrupt(
            node_id=interrupted.interrupt.node_id,
            phase=interrupted.interrupt.phase,
            reason=interrupted.interrupt.reason,
        )

        with _RUNS_LOCK:
            rec = _RUNS[run_id]
            rec.status = "paused"
            rec.paused_at = _now_utc()
            rec.completed_at = None
            rec.trace = tracer.steps()
            rec.error = None
            rec.checkpoint = checkpoint
            rec.pause_reason = "interrupt"
            rec.pending_interrupt = pending
            rec.pause_requested = False

        record.events.put(
            _format_sse(
                event="status",
                data={
                    "run_id": run_id,
                    "status": "paused",
                    "pause_reason": "interrupt",
                    "pending_interrupt": pending.model_dump(),
                },
            )
        )
        record.events.put(None)

    except RunPaused as paused:
        checkpoint = RunCheckpoint(
            run_id=run_id,
            created_at=_now_utc(),
            state=paused.checkpoint.state,
            completed_node_ids=list(paused.checkpoint.completed_node_ids),
            ready_node_ids=list(paused.checkpoint.ready_node_ids),
            indegree=dict(paused.checkpoint.indegree),
            handled_interrupts=list(paused.checkpoint.handled_interrupts),
        )

        with _RUNS_LOCK:
            rec = _RUNS[run_id]
            rec.status = "paused"
            rec.paused_at = _now_utc()
            rec.completed_at = None
            rec.trace = tracer.steps()
            rec.error = None
            rec.checkpoint = checkpoint
            rec.pause_reason = "manual"
            rec.pending_interrupt = None

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
            rec.pause_reason = None
            rec.pending_interrupt = None
            rec.checkpoint = None

            RUN_HISTORY_STORE.persist_terminal(
                run_id=rec.run_id,
                status="failed",
                started_at=rec.started_at,
                completed_at=rec.completed_at,
                trace=rec.trace,
                error=rec.error,
            )

        record.events.put(
            _format_sse(event="status", data={"run_id": run_id, "status": "failed", "error": str(exc)})
        )
        record.events.put(None)


async def _resume_run(run_id: str) -> None:
    with _RUNS_LOCK:
        record = _RUNS[run_id]
        request = record.request
        checkpoint = record.checkpoint

    if checkpoint is None:
        raise RuntimeError("Cannot resume without a checkpoint")

    def _emit_step(step: StepTrace) -> None:
        record.events.put(_format_sse(event="step", data=step.model_dump()))

    tracer = StepTracer.from_existing(record.trace, on_record=_emit_step)

    def _should_pause() -> bool:
        with _RUNS_LOCK:
            rec = _RUNS.get(run_id)
            return bool(rec is not None and rec.pause_requested)

    def _should_cancel() -> bool:
        with _RUNS_LOCK:
            rec = _RUNS.get(run_id)
            return bool(rec is not None and rec.cancel_requested)

    try:
        plan = parse_graph(request.graph)
        topological_sort(plan)

        nodes = build_nodes_for_graph(run_id=run_id, graph_nodes=request.graph.nodes)
        executor = AsyncExecutor()

        exec_checkpoint = ExecutionCheckpoint(
            state=dict(checkpoint.state),
            completed_node_ids=list(checkpoint.completed_node_ids),
            ready_node_ids=list(checkpoint.ready_node_ids),
            indegree=dict(checkpoint.indegree),
            handled_interrupts=list(checkpoint.handled_interrupts),
        )

        await executor.run(
            plan,
            nodes,
            checkpoint=exec_checkpoint,
            tracer=tracer,
            should_pause=_should_pause,
            should_cancel=_should_cancel,
        )

        with _RUNS_LOCK:
            rec = _RUNS[run_id]
            rec.status = "completed"
            rec.paused_at = None
            rec.completed_at = _now_utc()
            rec.trace = tracer.steps()
            rec.error = None
            rec.pause_reason = None
            rec.pending_interrupt = None
            rec.checkpoint = None

        record.events.put(_format_sse(event="status", data={"run_id": run_id, "status": "completed"}))
        record.events.put(None)

    except RunCancelled:
        with _RUNS_LOCK:
            rec = _RUNS[run_id]
            rec.status = "cancelled"
            rec.pause_requested = False
            rec.cancel_requested = False
            rec.paused_at = None
            rec.completed_at = _now_utc()
            rec.trace = tracer.steps()
            rec.error = None
            rec.checkpoint = None
            rec.pause_reason = None
            rec.pending_interrupt = None

        record.events.put(_format_sse(event="status", data={"run_id": run_id, "status": "cancelled"}))
        record.events.put(None)

    except RunInterrupted as interrupted:
        new_checkpoint = RunCheckpoint(
            run_id=run_id,
            created_at=_now_utc(),
            state=interrupted.checkpoint.state,
            completed_node_ids=list(interrupted.checkpoint.completed_node_ids),
            ready_node_ids=list(interrupted.checkpoint.ready_node_ids),
            indegree=dict(interrupted.checkpoint.indegree),
            handled_interrupts=list(interrupted.checkpoint.handled_interrupts),
        )

        pending = PendingInterrupt(
            node_id=interrupted.interrupt.node_id,
            phase=interrupted.interrupt.phase,
            reason=interrupted.interrupt.reason,
        )

        with _RUNS_LOCK:
            rec = _RUNS[run_id]
            rec.status = "paused"
            rec.paused_at = _now_utc()
            rec.completed_at = None
            rec.trace = tracer.steps()
            rec.error = None
            rec.checkpoint = new_checkpoint
            rec.pause_reason = "interrupt"
            rec.pending_interrupt = pending
            rec.pause_requested = False

        record.events.put(
            _format_sse(
                event="status",
                data={
                    "run_id": run_id,
                    "status": "paused",
                    "pause_reason": "interrupt",
                    "pending_interrupt": pending.model_dump(),
                },
            )
        )
        record.events.put(None)

    except RunPaused as paused:
        new_checkpoint = RunCheckpoint(
            run_id=run_id,
            created_at=_now_utc(),
            state=paused.checkpoint.state,
            completed_node_ids=list(paused.checkpoint.completed_node_ids),
            ready_node_ids=list(paused.checkpoint.ready_node_ids),
            indegree=dict(paused.checkpoint.indegree),
            handled_interrupts=list(paused.checkpoint.handled_interrupts),
        )

        with _RUNS_LOCK:
            rec = _RUNS[run_id]
            rec.status = "paused"
            rec.paused_at = _now_utc()
            rec.completed_at = None
            rec.trace = tracer.steps()
            rec.error = None
            rec.checkpoint = new_checkpoint
            rec.pause_reason = "manual"
            rec.pending_interrupt = None

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
            rec.pause_reason = None
            rec.pending_interrupt = None
            rec.checkpoint = None

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
    record = _RunRecord(run_id=run_id, status="running", started_at=_now_utc(), request=request)

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
        pause_reason=record.pause_reason,
        pending_interrupt=record.pending_interrupt,
    )


class RunControlResponse(BaseModel):
    run_id: str
    status: RunStatus


class RunControlStateResponse(RunControlResponse):
    pause_reason: PauseReason | None = None
    pending_interrupt: PendingInterrupt | None = None
    error: str | None = None


def _control_state_for(record: _RunRecord) -> RunControlStateResponse:
    return RunControlStateResponse(
        run_id=record.run_id,
        status=record.status,
        pause_reason=record.pause_reason,
        pending_interrupt=record.pending_interrupt,
        error=record.error,
    )


def _get_run_record_or_404(run_id: str) -> _RunRecord:
    record = _RUNS.get(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail="run_id not found")
    return record


def _request_pause_locked(record: _RunRecord) -> _RunRecord:
    # Idempotent: pausing a paused/completed/failed/cancelled run does nothing.
    if record.status == "running":
        record.pause_requested = True
    return record


def _request_cancel_locked(record: _RunRecord) -> _RunRecord:
    # Idempotent: cancelling a cancelled/completed/failed run does nothing.
    if record.status == "running":
        record.cancel_requested = True
        record.pause_requested = False
    elif record.status == "paused":
        record.status = "cancelled"
        record.pause_requested = False
        record.cancel_requested = False
        record.paused_at = None
        record.completed_at = _now_utc()
        record.error = None
        record.checkpoint = None
        record.pause_reason = None
        record.pending_interrupt = None

        RUN_HISTORY_STORE.persist_terminal(
            run_id=record.run_id,
            status="cancelled",
            started_at=record.started_at,
            completed_at=record.completed_at,
            trace=record.trace,
            error=record.error,
        )

        # Provide a fresh stream for SSE clients to observe the terminal status.
        record.events = queue.Queue()
        record.events.put(_format_sse(event="status", data={"run_id": record.run_id, "status": "cancelled"}))
        record.events.put(None)

    return record


@router.post("/api/run/{run_id}/pause", response_model=RunControlResponse)
async def pause_run(run_id: str) -> RunControlResponse:
    with _RUNS_LOCK:
        record = _get_run_record_or_404(run_id)
        record = _request_pause_locked(record)
        return RunControlResponse(run_id=record.run_id, status=record.status)


@router.post("/api/run/{run_id}/cancel", response_model=RunControlResponse)
async def cancel_run(run_id: str) -> RunControlResponse:
    with _RUNS_LOCK:
        record = _get_run_record_or_404(run_id)
        record = _request_cancel_locked(record)
        return RunControlResponse(run_id=record.run_id, status=record.status)


@router.post("/api/run/{run_id}/resume", response_model=RunControlResponse)
async def resume_run(run_id: str) -> RunControlResponse:
    with _RUNS_LOCK:
        record = _RUNS.get(run_id)

        if record is None:
            raise HTTPException(status_code=404, detail="run_id not found")

        if record.status != "paused":
            raise HTTPException(status_code=409, detail="run is not paused")

        if record.pause_reason == "interrupt" and record.pending_interrupt is not None:
            raise HTTPException(status_code=409, detail="run is awaiting a HITL decision")

        if record.checkpoint is None:
            raise HTTPException(status_code=409, detail="run has no checkpoint")

        record.status = "running"
        record.paused_at = None
        record.completed_at = None
        record.error = None
        record.pause_requested = False
        record.pause_reason = None
        record.pending_interrupt = None
        record.events = queue.Queue()

    _start_resume_worker(run_id)

    with _RUNS_LOCK:
        record = _RUNS[run_id]
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


class HitlEditRequest(BaseModel):
    state_patch: dict[str, Any] = Field(default_factory=dict)


def _start_resume_worker(run_id: str) -> None:
    def _runner() -> None:
        asyncio.run(_resume_run(run_id))

    threading.Thread(target=_runner, name=f"run-resume-{run_id}", daemon=True).start()


@router.post("/api/run/{run_id}/hitl/allow", response_model=RunControlResponse)
async def hitl_allow(run_id: str) -> RunControlResponse:
    with _RUNS_LOCK:
        record = _RUNS.get(run_id)
        if record is None:
            raise HTTPException(status_code=404, detail="run_id not found")

        if record.status != "paused" or record.pause_reason != "interrupt" or record.pending_interrupt is None:
            raise HTTPException(status_code=409, detail="run is not awaiting a HITL decision")

        if record.checkpoint is None:
            raise HTTPException(status_code=409, detail="run has no checkpoint")

        key = f"{record.pending_interrupt.phase}:{record.pending_interrupt.node_id}"
        handled = list(record.checkpoint.handled_interrupts)
        if key not in handled:
            handled.append(key)
        record.checkpoint.handled_interrupts = handled

        record.status = "running"
        record.paused_at = None
        record.completed_at = None
        record.error = None
        record.pause_requested = False
        record.pause_reason = None
        record.pending_interrupt = None
        record.events = queue.Queue()

    _start_resume_worker(run_id)

    with _RUNS_LOCK:
        record = _RUNS[run_id]
        return RunControlResponse(run_id=record.run_id, status=record.status)


@router.post("/api/run/{run_id}/hitl/edit", response_model=RunControlResponse)
async def hitl_edit(run_id: str, request: HitlEditRequest) -> RunControlResponse:
    with _RUNS_LOCK:
        record = _RUNS.get(run_id)
        if record is None:
            raise HTTPException(status_code=404, detail="run_id not found")

        if record.status != "paused" or record.pause_reason != "interrupt" or record.pending_interrupt is None:
            raise HTTPException(status_code=409, detail="run is not awaiting a HITL decision")

        if record.checkpoint is None:
            raise HTTPException(status_code=409, detail="run has no checkpoint")

        # Apply patch deterministically: shallow update of checkpoint state.
        patched_state = dict(record.checkpoint.state)
        patched_state.update(request.state_patch)
        record.checkpoint.state = patched_state

        key = f"{record.pending_interrupt.phase}:{record.pending_interrupt.node_id}"
        handled = list(record.checkpoint.handled_interrupts)
        if key not in handled:
            handled.append(key)
        record.checkpoint.handled_interrupts = handled

        record.status = "running"
        record.paused_at = None
        record.completed_at = None
        record.error = None
        record.pause_requested = False
        record.pause_reason = None
        record.pending_interrupt = None
        record.events = queue.Queue()

    _start_resume_worker(run_id)

    with _RUNS_LOCK:
        record = _RUNS[run_id]
        return RunControlResponse(run_id=record.run_id, status=record.status)


@router.post("/api/run/{run_id}/hitl/reject", response_model=RunControlResponse)
async def hitl_reject(run_id: str) -> RunControlResponse:
    with _RUNS_LOCK:
        record = _RUNS.get(run_id)
        if record is None:
            raise HTTPException(status_code=404, detail="run_id not found")

        if record.status != "paused" or record.pause_reason != "interrupt" or record.pending_interrupt is None:
            raise HTTPException(status_code=409, detail="run is not awaiting a HITL decision")

        record.status = "cancelled"
        record.pause_requested = False
        record.cancel_requested = False
        record.paused_at = None
        record.completed_at = _now_utc()
        record.error = None
        record.checkpoint = None
        record.pause_reason = None
        record.pending_interrupt = None

        record.events = queue.Queue()
        record.events.put(_format_sse(event="status", data={"run_id": run_id, "status": "cancelled"}))
        record.events.put(None)

        return RunControlResponse(run_id=record.run_id, status=record.status)


class WsControlCommand(BaseModel):
    action: Literal[
        "status",
        "pause",
        "resume",
        "cancel",
        "hitl_allow",
        "hitl_edit",
        "hitl_reject",
    ]
    state_patch: dict[str, Any] = Field(default_factory=dict)


class WsControlResponse(BaseModel):
    ok: bool
    state: RunControlStateResponse | None = None
    error: str | None = None


@router.websocket("/api/run/{run_id}/control")
async def control_ws(websocket: WebSocket, run_id: str) -> None:
    await websocket.accept()

    # Keep message loop simple and explicit.
    with _RUNS_LOCK:
        record = _RUNS.get(run_id)
        if record is None:
            await websocket.send_json(WsControlResponse(ok=False, error="run_id not found").model_dump())
            await websocket.close(code=1008)
            return

        await websocket.send_json(WsControlResponse(ok=True, state=_control_state_for(record)).model_dump())

    while True:
        try:
            raw = await websocket.receive_json()
        except WebSocketDisconnect:
            break
        except Exception:  # noqa: BLE001
            await websocket.send_json(WsControlResponse(ok=False, error="invalid JSON message").model_dump())
            continue

        try:
            cmd = WsControlCommand.model_validate(raw)
        except Exception as exc:  # noqa: BLE001
            await websocket.send_json(WsControlResponse(ok=False, error=str(exc)).model_dump())
            continue

        try:
            if cmd.action == "status":
                with _RUNS_LOCK:
                    record = _get_run_record_or_404(run_id)
                    await websocket.send_json(WsControlResponse(ok=True, state=_control_state_for(record)).model_dump())
                continue

            if cmd.action == "pause":
                with _RUNS_LOCK:
                    record = _get_run_record_or_404(run_id)
                    record = _request_pause_locked(record)
                    await websocket.send_json(WsControlResponse(ok=True, state=_control_state_for(record)).model_dump())
                continue

            if cmd.action == "cancel":
                with _RUNS_LOCK:
                    record = _get_run_record_or_404(run_id)
                    record = _request_cancel_locked(record)
                    await websocket.send_json(WsControlResponse(ok=True, state=_control_state_for(record)).model_dump())
                continue

            if cmd.action == "resume":
                # Reuse HTTP behavior.
                resp = await resume_run(run_id)
                with _RUNS_LOCK:
                    record = _get_run_record_or_404(run_id)
                    await websocket.send_json(
                        WsControlResponse(ok=True, state=_control_state_for(record)).model_dump()
                    )
                _ = resp
                continue

            if cmd.action == "hitl_allow":
                resp = await hitl_allow(run_id)
                with _RUNS_LOCK:
                    record = _get_run_record_or_404(run_id)
                    await websocket.send_json(
                        WsControlResponse(ok=True, state=_control_state_for(record)).model_dump()
                    )
                _ = resp
                continue

            if cmd.action == "hitl_edit":
                resp = await hitl_edit(run_id, HitlEditRequest(state_patch=cmd.state_patch))
                with _RUNS_LOCK:
                    record = _get_run_record_or_404(run_id)
                    await websocket.send_json(
                        WsControlResponse(ok=True, state=_control_state_for(record)).model_dump()
                    )
                _ = resp
                continue

            if cmd.action == "hitl_reject":
                resp = await hitl_reject(run_id)
                with _RUNS_LOCK:
                    record = _get_run_record_or_404(run_id)
                    await websocket.send_json(
                        WsControlResponse(ok=True, state=_control_state_for(record)).model_dump()
                    )
                _ = resp
                continue

            await websocket.send_json(WsControlResponse(ok=False, error="unsupported action").model_dump())

        except HTTPException as exc:
            await websocket.send_json(WsControlResponse(ok=False, error=str(exc.detail)).model_dump())
        except Exception as exc:  # noqa: BLE001
            await websocket.send_json(WsControlResponse(ok=False, error=str(exc)).model_dump())


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
