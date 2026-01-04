# F00003_S006: Playwright Browser Node - Navigation & Actions

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Add a minimal `browser` node that can perform core actions needed by the MVP:
- navigate to a URL
- click an element (by selector or SoM index)
- type text into an input

## Tasks
- [x] Add action helpers (navigate/click/type)
- [x] Implement `BrowserNode` using `BrowserSessionManager`
- [x] Add unit tests using fakes (no real Playwright required)
- [x] Update feature doc + changelog

## Implementation Notes
- This story uses small protocols (`BrowserPageLike`) so unit tests do not require Playwright.
- SoM clicking resolves `som_index` via `state['som_index_to_selector']` mapping.
- The runner does not yet provide a run-scoped context to nodes, so `run_id` and a `session_factory` are injected at construction time.

## Files Changed
- `backend/nodes/browser/actions.py`
- `backend/nodes/browser/node.py`
- `backend/tests/test_nodes_browser_actions.py`
- `backend/tests/test_nodes_browser_node.py`
- `.implementation/F00003_core_node_library/F00003_S006_playwright_browser_node_navigation_and_actions.md`

## Testing
- `cd backend && poetry run pytest -q`

## Blockers / Questions
- Later stories should introduce an `ExecutionContext` (run_id, shared services) passed into node execution so `BrowserNode` can be instantiated from graph config alone.
