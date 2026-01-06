# F00010_S004: Add Test-Mode Example Run Payload

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-06
**Updated:** 2026-01-06

## Goal

Add a `mode="test"` example request payload so developers can run the example workflow deterministically (no real HTTP/browser activity required).

## Acceptance Criteria

- A request body exists at `.examples/requests/run_bug_bounty_test.json`.
- `.examples/README.md` documents how to use it from Windows PowerShell.
- A smoke run via `POST /api/run` completes successfully with `status="completed"`.

## Tasks

- [x] Add `.examples/requests/run_bug_bounty_test.json`
- [x] Update `.examples/README.md`
- [x] Run one API smoke test in `mode="test"` and record result
- [x] Update changelog

## Files Changed

- `.examples/requests/run_bug_bounty_test.json`
- `.examples/README.md`

## Testing

- `docker compose up -d`
- `curl.exe -s -X POST http://localhost:36301/api/run -H "Content-Type: application/json" --data-binary "@.examples/requests/run_bug_bounty_test.json"`
