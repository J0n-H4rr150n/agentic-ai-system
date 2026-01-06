# F00010: Example Workspaces + Local Lab Target

**Status:** 🟢 Complete
**Phase:** 2
**Priority:** P1 (High)
**Target:** 2026-01-06

## Overview

Add first-class, runnable example graphs/workspaces and a safe local lab target service so we can test security/bug-bounty-style agent flows end-to-end without inventing missing tooling.

This feature is explicitly constrained to:
- Only use node types and config fields that exist and are wired.
- Keep the lab target safe (no intentionally vulnerable app shipped in-repo).
- Keep ports within the repo policy `36300–36399`.

## Stories

- [x] S001: Add Safe Local Lab Target Service
- [x] S002: Add Runnable Example Workflow Graphs (API-ready)
- [x] S003: Document Repeatable Run Path (Windows-friendly)
- [x] S004: Add Test-Mode Example Run Payload

## Acceptance Criteria

- A `lab-target` service is available via Docker Compose at `http://localhost:36303/`.
- Example graphs are present under `.examples/` and runnable via existing API endpoints:
  - `POST /api/workflow` expects `{ "graph": ... }`
  - `POST /api/run` expects `{ "graph": ..., "mode": ... }`
- The example workflow uses only wired nodes (e.g., `start`, `browser`, `http_request`, `http_fuzzer`, `llm`, `parallel_gate`, `end`).
- Docs provide copy/pasteable commands for Windows PowerShell.

## Technical Notes

- The backend “browser” node uses an httpx-backed page implementation in Docker/test contexts; the lab target should be reachable from containers.

## Related Files

- `docker-compose.yml`
- `.examples/`
- `lab-target/`
