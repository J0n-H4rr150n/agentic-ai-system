# F00003_S007: Playwright Browser Node - Observation Modes

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Add observation modes to the `browser` node so downstream nodes can choose the right data for:
- visual click decisions (screenshots)
- source inspection (cleaned HTML with extracted comments)
- traffic analysis (network log)

## Tasks
- [x] Add observation builder module with mode-specific outputs
- [x] Wire observation mode into `BrowserNode` output
- [x] Add unit tests using fakes (no real Playwright required)
- [x] Update feature doc + changelog

## Implementation Notes
- Keep Playwright optional by using protocols and fakes.
- Preserve the existing S006 action output keys (`action`, `ok`, `details`) under `output_key`.

## Files Changed
- `backend/nodes/browser/observation.py`
- `backend/nodes/browser/node.py`
- `backend/tests/test_nodes_browser_observation.py`
- `backend/tests/test_nodes_browser_node.py`
- `.implementation/F00003_core_node_library/F00003_S007_playwright_browser_node_observation_modes.md`
- `.implementation/F00003_core_node_library.md`
- `.implementation/changelog.md`

## Testing
- `cd backend && poetry run pytest -q`

## Blockers / Questions
- None.
