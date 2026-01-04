"""Workflow storage.

MVP: in-memory workflow store with version history.

This module is used by both API routes and node execution (nested workflows).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import threading
from uuid import uuid4

from backend.models.graph import GraphDefinition


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class WorkflowVersion:
    version: int
    created_at: datetime
    graph: GraphDefinition


@dataclass(slots=True)
class WorkflowRecord:
    workflow_id: str
    created_at: datetime
    updated_at: datetime
    versions: list[WorkflowVersion]


class WorkflowStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._workflows: dict[str, WorkflowRecord] = {}

    def create(self, graph: GraphDefinition) -> str:
        workflow_id = str(uuid4())
        now = _now_utc()
        record = WorkflowRecord(
            workflow_id=workflow_id,
            created_at=now,
            updated_at=now,
            versions=[WorkflowVersion(version=1, created_at=now, graph=graph)],
        )

        with self._lock:
            self._workflows[workflow_id] = record

        return workflow_id

    def create_version(self, workflow_id: str, graph: GraphDefinition) -> int:
        now = _now_utc()

        with self._lock:
            record = self._workflows.get(workflow_id)
            if record is None:
                raise KeyError(workflow_id)

            next_version = (record.versions[-1].version + 1) if record.versions else 1
            record.versions.append(WorkflowVersion(version=next_version, created_at=now, graph=graph))
            record.updated_at = now

        return next_version

    def get(self, workflow_id: str, *, version: int | None = None) -> tuple[WorkflowRecord, WorkflowVersion]:
        with self._lock:
            record = self._workflows.get(workflow_id)

        if record is None:
            raise KeyError(workflow_id)
        if not record.versions:
            raise RuntimeError("workflow has no versions")

        if version is None:
            return record, record.versions[-1]

        found = next((v for v in record.versions if v.version == version), None)
        if found is None:
            raise KeyError(f"{workflow_id}:{version}")

        return record, found

    def list_versions(self, workflow_id: str) -> tuple[int, list[WorkflowVersion]]:
        with self._lock:
            record = self._workflows.get(workflow_id)

        if record is None:
            raise KeyError(workflow_id)

        latest = record.versions[-1].version if record.versions else 0
        return latest, list(record.versions)

    def list(self) -> list[WorkflowRecord]:
        with self._lock:
            records = list(self._workflows.values())

        records.sort(key=lambda r: r.updated_at, reverse=True)
        return records


WORKFLOW_STORE = WorkflowStore()
