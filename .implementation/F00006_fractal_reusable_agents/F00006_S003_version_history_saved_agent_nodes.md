# F00006_S003: Version History for Saved Agent Nodes

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-04
**Updated:** 2026-01-04

## Goal
Add minimal backend support for versioning saved workflows so a workflow id can have multiple versions and clients can list and load specific versions.

## Acceptance Criteria
- A workflow has versions starting at 1.
- A new version can be created for an existing workflow id.
- Version history can be listed for a workflow id.
- A workflow can be fetched by id at the latest version (default) or a specific version (query param).
- Backend unit tests cover version create/list/get behavior.

## Scope
- Backend-only API changes (no frontend UI changes in this story).
- In-memory persistence remains acceptable for MVP.

## Tasks
- [x] Create story branch + story doc
- [x] Extend workflow storage model to support versions
- [x] Add endpoints for create version + list versions
- [x] Add `version` query param to get workflow
- [x] Add/update backend tests
- [x] Update feature doc + changelog; mark story complete

## Files Changed
- `backend/api/routes/workflow.py` - Versioned in-memory workflow store and added version endpoints
- `backend/tests/test_workflow_api.py` - Added tests for version create/list/get behaviors
- `.implementation/F00006_fractal_reusable_agents.md` - Checked off S003
- `.implementation/changelog.md` - Added S003 entry
- `.implementation/F00006_fractal_reusable_agents/F00006_S003_version_history_saved_agent_nodes.md` - Story status/tasks/files

## Implementation Notes
- Kept `POST /api/workflow` semantics (creates a new workflow id) to avoid breaking the existing frontend Save-as-Node flow.
- Added explicit endpoints for version creation and listing; `GET /api/workflow/{workflow_id}` defaults to latest version but supports `?version=`.

## Testing
- `cd backend && poetry run pytest -k workflow`

## Blockers / Questions
- None
