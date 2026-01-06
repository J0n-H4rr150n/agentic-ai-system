# F00010_S003: Document Repeatable Run Path (Windows-friendly)

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-06
**Updated:** 2026-01-06

## Goal

Document a repeatable workflow for running the example graphs end-to-end on Windows, including Docker Compose, API calls, and expected outputs.

## Acceptance Criteria

- `.examples/README.md` contains PowerShell-friendly commands.
- Docs specify the local `lab-target` default URL and port.
- Docs avoid claiming unsupported UI capabilities (e.g., importing saved workflows into canvas if not implemented).

## Tasks

- [x] Add `.examples/README.md` with PowerShell commands and request file references
- [x] Document that the API expects `{ "graph": ... }`
- [x] Document `lab-target` default URL/port
- [ ] Add a short note about Docker networking (container-to-container vs host) if needed
- [x] Update changelog after story completion

## Files Changed

- `.examples/README.md`

## Testing

- Follow `.examples/README.md` end-to-end.

## Blockers / Questions

- None.
