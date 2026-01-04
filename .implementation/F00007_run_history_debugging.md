# F00007: Run History & Debugging

**Status:** 🟡 In Progress
**Phase:** 6
**Priority:** P1 (High)

## Overview
Add persistence and UI to browse past runs and debug executions beyond the live trace viewer.

## Stories
- [x] S001: Persist run metadata + step traces
- [ ] S002: Run list view (per workflow)
- [ ] S003: Run detail view (tree/steps, inputs/outputs, screenshots)
- [ ] S004: Replay from checkpoint (time-travel)
- [ ] S005: Filter/search by status and node type

## Acceptance Criteria
- Completed runs are discoverable and can be reopened later.
- Run detail view renders the same step information as the live trace viewer.
- Users can replay from a checkpoint (where available).

## Technical Notes
- Live trace viewer exists; this feature focuses on persistence + navigation.
- Checkpointing is a dependency for replay.

## Related Files
- `backend/models/run.py`
- `backend/api/routes/run.py`
- `frontend/public/js/ui/trace/*`
