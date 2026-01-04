# F00004_S005: Build Sample Security Workflow

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Provide a built-in sample workflow on the canvas matching the MVP story: Start → Browser → LLM → Router → End.

## Acceptance Criteria
- On page load, the canvas contains a sample workflow graph:
  - Start → Browser → LLM → Router → End
- Browser node is preconfigured with a target URL (via Start state + Browser `url_key`)
- The graph is runnable via the existing Run button (even if nodes are stubbed in backend for now)

## Tasks
- [x] Add a sample workflow builder module (pure, testable)
- [x] Load the sample workflow in `CanvasManager` initialization
- [x] Add unit tests for the sample workflow structure
- [x] Update feature doc + changelog

## Implementation Notes
- Keep UX minimal: no new buttons/menus; the sample graph loads by default.
- Use deterministic node ids and default port ids to wire edges reliably.

## Files Changed
- `frontend/public/js/graph/sample-workflows.js`
- `frontend/public/js/nodes/index.js`
- `frontend/public/js/wires/index.js`
- `frontend/public/js/canvas/index.js`
- `frontend/tests/graph/sample-workflows.test.js`
- `.implementation/F00004_integration_first_run/F00004_S005_build_sample_security_workflow.md`
- `.implementation/F00004_integration_first_run.md`
- `.implementation/changelog.md`

## Testing
- `cd frontend && npm test`

## Blockers / Questions
- None
