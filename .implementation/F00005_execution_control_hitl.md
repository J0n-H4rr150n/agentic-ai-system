# F00005: Execution Control & Human-in-the-Loop

**Status:** 🟡 In Progress
**Phase:** 4
**Priority:** P0 (Critical)

## Overview
Add runtime execution control (pause/resume/stop) and human-in-the-loop approvals for risky steps.

This feature is the bridge from “runs complete end-to-end” to “runs can be supervised safely and iteratively”.

## Stories
- [x] S001: Interrupt point configuration on nodes
- [x] S002: Persist checkpoint + pause execution
- [x] S003: Resume execution from checkpoint
- [x] S004: Force-stop mechanism (cancel run)
- [x] S005: Human-in-the-loop actions: Allow / Edit / Reject
- [x] S006: Runtime control channel (WebSocket) for 2-way control

## Acceptance Criteria
- User can pause a running graph and later resume it.
- A node can be configured as an interrupt point; execution halts and awaits a human decision.
- Human decisions are applied deterministically (Allow continues, Edit updates node inputs/state, Reject stops run).
- Runs can be force-stopped and transition to a terminal state.

## Technical Notes
- Requires durable checkpoint storage (Redis) and run state model updates.
- WebSocket is preferred for bidirectional control; SSE can remain for step streaming.
- All inputs from UI must be validated (Pydantic) and recorded in trace/audit fields.

## Related Files
- `backend/api/routes/run.py`
- `backend/runner/executor.py`
- `backend/runner/checkpoint.py`
- `frontend/public/js/ui/run-controls.js`
- `frontend/public/js/ui/trace/*`
