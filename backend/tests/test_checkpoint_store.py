from __future__ import annotations

from datetime import datetime, timezone

import pytest

from backend.models.run import RunCheckpoint
from backend.runner.checkpoint import InMemoryCheckpointStore, RedisCheckpointStore


class _FakeRedis:
    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    def set(self, key: str, value: str) -> None:
        self._data[key] = value

    def get(self, key: str):  # noqa: ANN001
        return self._data.get(key)

    def delete(self, key: str) -> None:
        self._data.pop(key, None)


def _checkpoint(run_id: str) -> RunCheckpoint:
    return RunCheckpoint(
        run_id=run_id,
        created_at=datetime(2026, 1, 5, tzinfo=timezone.utc),
        state={"a": 1},
        completed_node_ids=["n1"],
        ready_node_ids=["n2"],
        indegree={"n2": 0},
        handled_interrupts=[],
    )


def test_in_memory_checkpoint_store_roundtrip() -> None:
    store = InMemoryCheckpointStore()
    cp = _checkpoint("r1")

    assert store.load("r1") is None

    store.save("r1", cp)
    loaded = store.load("r1")
    assert loaded is not None
    assert loaded.run_id == "r1"
    assert loaded.state == {"a": 1}

    store.delete("r1")
    assert store.load("r1") is None


def test_redis_checkpoint_store_roundtrip() -> None:
    fake = _FakeRedis()
    store = RedisCheckpointStore(fake)
    cp = _checkpoint("r2")

    store.save("r2", cp)
    loaded = store.load("r2")
    assert loaded is not None
    assert loaded.model_dump() == cp.model_dump()

    store.delete("r2")
    assert store.load("r2") is None


def test_redis_checkpoint_store_rejects_non_string_payload() -> None:
    class _BadRedis(_FakeRedis):
        def get(self, key: str):  # noqa: ANN001
            return 123

    store = RedisCheckpointStore(_BadRedis())
    store.save("r3", _checkpoint("r3"))

    with pytest.raises(TypeError, match="non-string"):
        store.load("r3")
