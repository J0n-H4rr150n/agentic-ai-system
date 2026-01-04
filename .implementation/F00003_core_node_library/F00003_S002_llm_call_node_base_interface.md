# F00003_S002: LLM Call Node - Base Interface

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Create a provider-agnostic LLM interface and a minimal `llm` node implementation that can be backed by different providers (Vertex AI first).

## Tasks
- [x] Create `backend/nodes/llm/` package
- [x] Define provider-agnostic `LLMClient` protocol and normalized response models
- [x] Implement `LLMCallNode` using injected client
- [x] Add unit tests for prompt sourcing, json mode, and validation
- [x] Update feature doc + changelog

## Implementation Notes
- This story does not add a provider SDK dependency.
- `LLMCallNode` follows the current `BaseNode.execute(state)->dict` contract by taking `config` at construction time.
- JSON mode is supported by parsing JSON from provider text if the provider does not return a structured JSON object.

## Files Changed
- `backend/nodes/llm/__init__.py`
- `backend/nodes/llm/base.py`
- `backend/tests/test_nodes_llm_base.py`
- `.implementation/F00003_core_node_library/F00003_S002_llm_call_node_base_interface.md`

## Testing
- `cd backend && poetry run pytest -q`

## Blockers / Questions
- None
