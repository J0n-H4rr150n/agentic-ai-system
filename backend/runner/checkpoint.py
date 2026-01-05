"""Checkpoint persistence.

This module provides a small abstraction for storing and retrieving run checkpoints.

Default behavior is in-memory storage for tests and MVP; if `REDIS_URL` is set,
callers can opt into Redis-backed persistence.
"""

from __future__ import annotations

import os
import threading
from typing import Any, Protocol

from backend.models.run import RunCheckpoint


class CheckpointStore(Protocol):
    def save(self, run_id: str, checkpoint: RunCheckpoint) -> None: ...

    def load(self, run_id: str) -> RunCheckpoint | None: ...

    def delete(self, run_id: str) -> None: ...


class InMemoryCheckpointStore:
    """Thread-safe in-memory checkpoint store."""

    def __init__(self) -> None:
        self._by_run_id: dict[str, RunCheckpoint] = {}
        self._lock = threading.Lock()

    def save(self, run_id: str, checkpoint: RunCheckpoint) -> None:
        if not isinstance(run_id, str) or not run_id:
            raise ValueError("run_id must be a non-empty string")
        if not isinstance(checkpoint, RunCheckpoint):
            raise TypeError("checkpoint must be a RunCheckpoint")

        with self._lock:
            self._by_run_id[run_id] = checkpoint

    def load(self, run_id: str) -> RunCheckpoint | None:
        if not isinstance(run_id, str) or not run_id:
            raise ValueError("run_id must be a non-empty string")

        with self._lock:
            return self._by_run_id.get(run_id)

    def delete(self, run_id: str) -> None:
        if not isinstance(run_id, str) or not run_id:
            raise ValueError("run_id must be a non-empty string")

        with self._lock:
            self._by_run_id.pop(run_id, None)


class RedisCheckpointStore:
    """Redis-backed checkpoint store.

    The Redis client is injected for testability. It must support `get`, `set`, and
    `delete` methods compatible with redis-py.
    """

    def __init__(self, client: Any, *, key_prefix: str = "checkpoint:") -> None:
        if client is None:
            raise ValueError("client must be provided")
        if not isinstance(key_prefix, str) or not key_prefix:
            raise ValueError("key_prefix must be a non-empty string")

        self._client = client
        self._key_prefix = key_prefix

    def _key(self, run_id: str) -> str:
        return f"{self._key_prefix}{run_id}"

    def save(self, run_id: str, checkpoint: RunCheckpoint) -> None:
        if not isinstance(run_id, str) or not run_id:
            raise ValueError("run_id must be a non-empty string")
        if not isinstance(checkpoint, RunCheckpoint):
            raise TypeError("checkpoint must be a RunCheckpoint")

        payload = checkpoint.model_dump_json()
        self._client.set(self._key(run_id), payload)

    def load(self, run_id: str) -> RunCheckpoint | None:
        if not isinstance(run_id, str) or not run_id:
            raise ValueError("run_id must be a non-empty string")

        raw = self._client.get(self._key(run_id))
        if raw is None:
            return None
        if isinstance(raw, (bytes, bytearray)):
            raw = raw.decode("utf-8")
        if not isinstance(raw, str):
            raise TypeError("Redis returned a non-string value for checkpoint")

        return RunCheckpoint.model_validate_json(raw)

    def delete(self, run_id: str) -> None:
        if not isinstance(run_id, str) or not run_id:
            raise ValueError("run_id must be a non-empty string")

        self._client.delete(self._key(run_id))


def build_checkpoint_store_from_env(*, env: dict[str, str] | None = None) -> CheckpointStore:
    """Build a checkpoint store from environment.

    If `REDIS_URL` is set, returns a RedisCheckpointStore. Otherwise, returns
    an InMemoryCheckpointStore.
    """

    environ = env if env is not None else os.environ
    redis_url = environ.get("REDIS_URL")
    if not redis_url:
        return InMemoryCheckpointStore()

    try:
        import redis  # type: ignore
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("REDIS_URL is set but redis package is not installed") from exc

    client = redis.Redis.from_url(redis_url)
    return RedisCheckpointStore(client)
