# F00002: State Machine Runner

**Status:** 🟡 In Progress
**Phase:** 1 (MVP)
**Priority:** P0 (Critical)
**Target:** Today

## Overview

Build the Python FastAPI backend that accepts a graph JSON payload and executes it as a state machine with parallel node support, state passing, and step-by-step tracing.

## Stories

- [x] S001: FastAPI Project Setup & Docker
- [x] S002: Pydantic Models for Graph Schema
- [x] S003: Graph Parser (JSON → Execution Plan)
- [x] S004: Dependency Resolver (Topological Sort)
- [x] S005: Base Node Executor Interface
- [x] S006: State Container Class
- [x] S007: Async Executor with Parallel Support
- [x] S008: Step Tracer (Input/Output/Duration)
- [x] S009: Run API Endpoints
- [ ] S010: SSE Streaming for Real-time Updates

## Acceptance Criteria

- [ ] `POST /api/run` accepts graph JSON, returns `run_id`
- [ ] `GET /api/run/{id}` returns execution status and trace
- [ ] `GET /api/run/{id}/stream` returns SSE stream of step updates
- [ ] Graph parser validates node types and edge connections
- [ ] Dependency resolver builds correct execution order
- [ ] Parallel-capable nodes execute concurrently via asyncio
- [ ] State object flows through graph (read/write per node)
- [ ] Each step logs: node_id, input, output, duration_ms, status
- [ ] Errors captured per-step, don't crash entire run

## Technical Notes

- Python 3.11+ with FastAPI + Pydantic v2
- asyncio for parallel execution (no threading)
- No LangGraph - custom state machine implementation
- Redis for checkpoint storage (mock with dict for MVP)
- All code follows file size guidelines (< 200 lines per file)

## Folder Structure

```
backend/
  ├── main.py                   # FastAPI entry point (~40 lines)
  ├── requirements.txt
  ├── pyproject.toml
  ├── api/
  │   ├── __init__.py
  │   ├── routes/
  │   │   ├── __init__.py
  │   │   ├── run.py            # POST/GET /api/run, SSE stream
  │   │   ├── workflow.py       # Workflow CRUD (future)
  │   │   └── health.py         # Health check endpoint
  │   └── deps.py               # Dependency injection (get_db, etc.)
  ├── runner/
  │   ├── __init__.py
  │   ├── graph_parser.py       # JSON → GraphDefinition
  │   ├── dependency.py         # Topological sort, execution order
  │   ├── executor.py           # AsyncExecutor - main loop
  │   ├── state.py              # StateContainer class
  │   ├── tracer.py             # StepTracer - logs each step
  │   └── checkpoint.py         # Checkpoint save/restore (Redis mock)
  ├── nodes/
  │   ├── __init__.py
  │   ├── base.py               # BaseNode abstract class
  │   ├── registry.py           # NodeRegistry - type → class mapping
  │   └── mock.py               # MockNode for testing
  ├── models/
  │   ├── __init__.py
  │   ├── graph.py              # GraphDefinition, NodeDef, EdgeDef
  │   ├── run.py                # RunStatus, StepTrace, RunResult
  │   └── state.py              # StateSchema, StateValue
  └── utils/
      ├── __init__.py
      └── sse.py                # SSE response helpers
```

## API Specification

### POST /api/run

Request:
```json
{
  "graph": {
    "nodes": [...],
    "edges": [...],
    "state_schema": {...}
  },
  "mode": "run" | "simulate" | "test"
}
```

Response:
```json
{
  "run_id": "uuid",
  "status": "running"
}
```

### GET /api/run/{id}

Response:
```json
{
  "run_id": "uuid",
  "status": "running" | "completed" | "failed" | "paused",
  "started_at": "ISO timestamp",
  "completed_at": "ISO timestamp or null",
  "current_step": "node-id or null",
  "trace": [
    {
      "step_id": 1,
      "node_id": "uuid",
      "node_type": "llm_call",
      "status": "completed",
      "started_at": "ISO",
      "completed_at": "ISO",
      "duration_ms": 1234,
      "input": {...},
      "output": {...},
      "error": null
    }
  ]
}
```

### GET /api/run/{id}/stream (SSE)

```
event: step_start
data: {"step_id": 1, "node_id": "uuid", "node_type": "browser"}

event: step_complete
data: {"step_id": 1, "duration_ms": 500, "output": {...}}

event: run_complete
data: {"status": "completed", "final_state": {...}}
```

## Dependencies

- F00001 (Canvas provides the JSON to execute)
