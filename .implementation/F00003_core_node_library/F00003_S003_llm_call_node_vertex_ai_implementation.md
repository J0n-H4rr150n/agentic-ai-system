# F00003_S003: LLM Call Node - Vertex AI Implementation

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Add a concrete Vertex AI (Gemini) implementation of the provider-agnostic `LLMClient` interface.

## Tasks
- [x] Add `VertexAILLMClient` implementing `LLMClient`
- [x] Keep provider SDK import lazy (tests run without real credentials)
- [x] Add unit tests using fakes (no network)
- [x] Update Poetry + `requirements.txt`
- [x] Update feature doc + changelog

## Implementation Notes
- `VertexAILLMClient` wraps the provider SDK call in `asyncio.to_thread(...)` to avoid blocking the event loop.
- Authentication is assumed via ADC; project/location are provided via `VertexAISettings`.
- JSON mode requests `response_mime_type="application/json"` and parses JSON from returned text.

## Files Changed
- `backend/nodes/llm/vertex.py`
- `backend/nodes/llm/config.py`
- `backend/tests/test_nodes_llm_vertex.py`
- `.implementation/F00003_core_node_library/F00003_S003_llm_call_node_vertex_ai_implementation.md`

## Testing
- `cd backend && poetry run pytest -q`

## Blockers / Questions
- None
