# F00006: Fractal Architecture (Reusable Agents)

**Status:** 🟡 In Progress
**Phase:** 5
**Priority:** P1 (High)

## Overview
Allow saving graphs as reusable “agent nodes” that appear in the palette with version history.

This enables composition: complex agents are built from smaller agents.

## Stories
- [x] S001: Persist workflows (save/load) in backend
- [x] S002: “Save as Node” action (frontend)
- [x] S003: Version history for saved agent nodes
- [ ] S004: Palette integration for saved agents
- [ ] S005: Nested execution (agent-within-agent)
- [ ] S006: Infer input/output schema from saved graphs

## Acceptance Criteria
- A workflow can be saved and loaded by id.
- A saved workflow can be executed as a single node inside another graph.
- Versioned saved agents can be selected and upgraded/downgraded.
- Palette displays saved agents without breaking existing built-in nodes.

## Technical Notes
- Requires a persistence layer (initially in-memory is acceptable only if explicitly scoped; target is Postgres).
- Nested execution must preserve tracing boundaries (parent run step references child run trace).

## Related Files
- `backend/api/routes/workflow.py`
- `backend/models/*`
- `frontend/public/js/graph/*`
- `frontend/public/js/palette/*`
