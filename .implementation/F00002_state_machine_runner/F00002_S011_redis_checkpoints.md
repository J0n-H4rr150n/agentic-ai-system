# F00002_S011: Redis Checkpoint Persistence

**Status:** 🟢 Complete
**Assignee:** AI Agent
**Created:** 2026-01-05
**Updated:** 2026-01-05

## Goal
Persist run checkpoints to Redis so pause/resume and replay workflows can survive beyond in-process memory.

## Scope
- Add a checkpointer abstraction with an in-memory default.
- Add Redis-backed implementation enabled via `REDIS_URL`.
- Integrate into run pause/interrupt/resume flows.

## Tasks
- [x] Add `backend/runner/checkpoint.py` with in-memory + Redis implementations
- [x] Wire checkpoint persistence into `backend/api/routes/run.py`
- [x] Add unit tests for checkpoint store
- [x] Update docs + changelog

## Implementation Notes
- Store checkpoints as JSON using `RunCheckpoint.model_dump_json()`.
- Redis keys: `checkpoint:{run_id}`.
- If Redis isn’t configured, default to in-memory store.

## Files Changed
- `backend/runner/checkpoint.py` - New checkpoint store abstraction + Redis implementation
- `backend/api/routes/run.py` - Persist/load/delete checkpoints via store
- `backend/tests/test_checkpoint_store.py` - Unit tests for checkpoint stores
- `backend/requirements.txt` - Add `redis`
- `backend/pyproject.toml` - Add `redis`
- `.implementation/F00002_state_machine_runner.md` - Track story and status
- `.implementation/F00002_state_machine_runner/F00002_S011_redis_checkpoints.md` - Story doc
- `.implementation/changelog.md` - Changelog entry

## Testing
- Backend: `make test-backend-docker`

## Blockers / Questions
- None
