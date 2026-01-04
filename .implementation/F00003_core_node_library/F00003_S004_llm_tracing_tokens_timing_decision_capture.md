# F00003_S004: LLM Tracing (tokens, timing, decision capture)

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Capture LLM-specific tracing fields (token counts, timing, and decision capture) in a consistent shape produced by the `llm` node.

## Tasks
- [x] Add `LLMTrace` model + helper functions
- [x] Record `elapsed_time_ms` around provider call
- [x] Include token usage (when provided) in trace
- [x] Extract decision fields (`llm_decision`, `llm_reasoning`, `llm_confidence`) from JSON payload
- [x] Add unit tests
- [x] Update feature doc + changelog

## Implementation Notes
- The runner already captures per-node duration in `StepTrace`; this story adds LLM-specific trace metadata.
- `LLMCallNode` now returns a `trace` object inside its output payload.

## Files Changed
- `backend/nodes/llm/tracing.py`
- `backend/nodes/llm/base.py`
- `backend/tests/test_nodes_llm_base.py`
- `backend/tests/test_nodes_llm_tracing.py`
- `.implementation/F00003_core_node_library/F00003_S004_llm_tracing_tokens_timing_decision_capture.md`

## Testing
- `cd backend && poetry run pytest -q`

## Blockers / Questions
- None
