# F00010_S002: Add Runnable Example Workflow Graphs (API-ready)

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-06
**Updated:** 2026-01-06

## Goal

Add example graphs/workspace payloads that can be saved and executed via the existing backend API, using only currently supported nodes/config keys.

## Acceptance Criteria

- Example graph JSON exists under `.examples/graphs/`.
- Example request bodies exist under `.examples/requests/`:
  - create workflow request `{ "graph": ... }`
  - run request `{ "graph": ..., "mode": "simulate" }`
- Example targets the local `lab-target` service by default (`http://localhost:36303/`).
- No invented nodes/tools; uses only wired node types.

## Tasks

- [x] Add bug-bounty-style example graph (`parallel_gate` fork/join, `browser`, `http_request`, `http_fuzzer`, `llm`)
- [x] Add API-ready request JSON files to avoid shell quoting
- [x] Add example workspace JSON wrapper (graph inlined)
- [ ] Add optional `mode="test"` variant for fully deterministic offline runs
- [x] Update changelog after story completion

## Implementation Notes

- `simulate` constraints are respected: browser action is `navigate`, HTTP methods are `GET`.
- The example does not assume UI can “import” a saved workflow into canvas; API is the reference path.

## Files Changed

- `.examples/graphs/bug_bounty_simulate_graph.json`
- `.examples/requests/create_workflow_bug_bounty_simulate.json`
- `.examples/requests/run_bug_bounty_simulate.json`
- `.examples/workspaces/bug_bounty_simulate_workspace.json`

## Testing

- Create workflow: `POST /api/workflow` with `.examples/requests/create_workflow_bug_bounty_simulate.json`
- Run simulate: `POST /api/run` with `.examples/requests/run_bug_bounty_simulate.json`

## Blockers / Questions

- None.
