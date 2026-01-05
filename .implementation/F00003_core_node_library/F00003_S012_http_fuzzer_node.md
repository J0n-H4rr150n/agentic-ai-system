# F00003_S012: HTTP Fuzzer Node

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-05
**Updated:** 2026-01-05

## Goal
Add an `http_fuzzer` node that can generate a batch of HTTP requests from a URL template and payload list, execute them, and return aggregated results for downstream analysis.

This is the Phase 3 "HTTP Fuzzer" checkbox in `.planning/plan.md`.

## Non-Goals (MVP)
- No LLM-driven loop inside the node.
- No advanced mutation strategies beyond `{payload}` substitution.
- No concurrency tuning or rate limiting.

## Tasks
- [x] Implement backend node `http_fuzzer`
- [x] Wire into node factory and schema inference
- [x] Add unit tests
- [x] Add palette entry
- [x] Update feature doc, plan checkbox, changelog; ship to `main`

## Implementation Notes
- Config uses `url_template`/`url_template_key` and `payloads`/`payloads_key`.
- Output is written to `output_key` (default: `http_fuzzer_output`) and includes `results` + `summary`.
- In `simulate` mode, enforce safe HTTP methods (`GET|HEAD|OPTIONS`).
- In `test` mode, stub results to avoid network.

## Files Changed
- `backend/nodes/http/fuzzer.py` - new `http_fuzzer` node
- `backend/runner/node_factory.py` - construct `http_fuzzer` (run/test/simulate)
- `backend/runner/mode_guard.py` - simulate guard wrapper
- `backend/runner/test_doubles.py` - test-mode stub fuzzer
- `backend/workflows/schema.py` - schema inference support
- `backend/tests/test_nodes_http_fuzzer.py` - node unit tests
- `backend/tests/test_run_modes.py` - mode behavior coverage for fuzzer
- `backend/tests/test_node_factory_modes.py` - unit coverage for simulate guard wrapping
- `backend/tests/test_node_registry.py` - registry/parser acceptance
- `frontend/public/js/palette/categories.js` - palette entry

## Testing
- `make test-backend-docker`
