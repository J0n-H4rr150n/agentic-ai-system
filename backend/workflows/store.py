"""Workflow storage.

This module is used by both API routes and node execution (nested workflows).

If `DATABASE_URL` is set, `WORKFLOW_STORE` will use Postgres; otherwise it
falls back to an in-memory store (useful for unit tests and local quick runs).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import os
import threading
from typing import Protocol, runtime_checkable
from uuid import uuid4

import sqlalchemy as sa

from backend.db.engine import create_db_engine, database_url
from backend.db.models import WorkflowRow, WorkflowVersionRow
from backend.models.graph import GraphDefinition


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_graph_json(graph_json: dict) -> dict:
    """Normalize persisted graph JSON for model validation.

    Pydantic uses an alias for EdgeDefinition.from_ -> "from". If a graph was
    dumped without aliases, edges may contain "from_" keys. Convert them.
    """

    edges = graph_json.get("edges")
    if not isinstance(edges, list):
        return graph_json

    mutated = False
    normalized_edges: list[dict] = []
    for edge in edges:
        if not isinstance(edge, dict):
            normalized_edges.append(edge)
            continue
        if "from" not in edge and "from_" in edge:
            edge = {**edge, "from": edge.get("from_")}
            edge.pop("from_", None)
            mutated = True
        normalized_edges.append(edge)

    if not mutated:
        return graph_json
    return {**graph_json, "edges": normalized_edges}


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


@runtime_checkable
class WorkflowStore(Protocol):
    def create(self, graph: GraphDefinition) -> str: ...

    def create_version(self, workflow_id: str, graph: GraphDefinition) -> int: ...

    def get(self, workflow_id: str, *, version: int | None = None) -> tuple[WorkflowRecord, WorkflowVersion]: ...

    def list_versions(self, workflow_id: str) -> tuple[int, list[WorkflowVersion]]: ...

    def list(self) -> list[WorkflowRecord]: ...


class InMemoryWorkflowStore:
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


class PostgresWorkflowStore:
    def __init__(self) -> None:
        self._engine = create_db_engine()

    def create(self, graph: GraphDefinition) -> str:
        workflow_id = str(uuid4())
        now = _now_utc()

        graph_json = (
            graph.model_dump(mode="json", by_alias=True)
            if hasattr(graph, "model_dump")
            else graph  # type: ignore[truthy-bool]
        )

        with self._engine.begin() as conn:
            conn.execute(
                sa.insert(WorkflowRow).values(workflow_id=workflow_id, created_at=now, updated_at=now)
            )
            conn.execute(
                sa.insert(WorkflowVersionRow).values(
                    workflow_id=workflow_id,
                    version=1,
                    created_at=now,
                    graph=graph_json,
                )
            )

        return workflow_id

    def create_version(self, workflow_id: str, graph: GraphDefinition) -> int:
        now = _now_utc()
        graph_json = (
            graph.model_dump(mode="json", by_alias=True)
            if hasattr(graph, "model_dump")
            else graph  # type: ignore[truthy-bool]
        )

        with self._engine.begin() as conn:
            exists = conn.execute(
                sa.select(sa.literal(True)).select_from(WorkflowRow).where(WorkflowRow.workflow_id == workflow_id)
            ).scalar_one_or_none()
            if not exists:
                raise KeyError(workflow_id)

            latest = conn.execute(
                sa.select(sa.func.max(WorkflowVersionRow.version)).where(WorkflowVersionRow.workflow_id == workflow_id)
            ).scalar_one()
            next_version = int(latest or 0) + 1

            conn.execute(
                sa.insert(WorkflowVersionRow).values(
                    workflow_id=workflow_id,
                    version=next_version,
                    created_at=now,
                    graph=graph_json,
                )
            )
            conn.execute(
                sa.update(WorkflowRow)
                .where(WorkflowRow.workflow_id == workflow_id)
                .values(updated_at=now)
            )

        return next_version

    def get(self, workflow_id: str, *, version: int | None = None) -> tuple[WorkflowRecord, WorkflowVersion]:
        with self._engine.connect() as conn:
            workflow_row = conn.execute(
                sa.select(
                    WorkflowRow.workflow_id,
                    WorkflowRow.created_at,
                    WorkflowRow.updated_at,
                ).where(WorkflowRow.workflow_id == workflow_id)
            ).one_or_none()
            if workflow_row is None:
                raise KeyError(workflow_id)

            if version is None:
                row = conn.execute(
                    sa.select(
                        WorkflowVersionRow.version,
                        WorkflowVersionRow.created_at,
                        WorkflowVersionRow.graph,
                    )
                    .where(WorkflowVersionRow.workflow_id == workflow_id)
                    .order_by(WorkflowVersionRow.version.desc())
                    .limit(1)
                ).one_or_none()
            else:
                row = conn.execute(
                    sa.select(
                        WorkflowVersionRow.version,
                        WorkflowVersionRow.created_at,
                        WorkflowVersionRow.graph,
                    )
                    .where(WorkflowVersionRow.workflow_id == workflow_id)
                    .where(WorkflowVersionRow.version == version)
                ).one_or_none()

            if row is None:
                if version is None:
                    raise RuntimeError("workflow has no versions")
                raise KeyError(f"{workflow_id}:{version}")

            graph_payload = _normalize_graph_json(row.graph)
            graph = GraphDefinition.model_validate(graph_payload)

            selected = WorkflowVersion(version=row.version, created_at=row.created_at, graph=graph)
            record = WorkflowRecord(
                workflow_id=workflow_row.workflow_id,
                created_at=workflow_row.created_at,
                updated_at=workflow_row.updated_at,
                versions=[selected],
            )

        return record, selected

    def list_versions(self, workflow_id: str) -> tuple[int, list[WorkflowVersion]]:
        with self._engine.connect() as conn:
            exists = conn.execute(
                sa.select(sa.literal(True)).select_from(WorkflowRow).where(WorkflowRow.workflow_id == workflow_id)
            ).scalar_one_or_none()
            if not exists:
                raise KeyError(workflow_id)

            rows = list(
                conn.execute(
                    sa.select(
                        WorkflowVersionRow.version,
                        WorkflowVersionRow.created_at,
                        WorkflowVersionRow.graph,
                    )
                    .where(WorkflowVersionRow.workflow_id == workflow_id)
                    .order_by(WorkflowVersionRow.version.asc())
                ).all()
            )

        versions = []
        for r in rows:
            graph_payload = _normalize_graph_json(r.graph)
            versions.append(
                WorkflowVersion(
                    version=r.version,
                    created_at=r.created_at,
                    graph=GraphDefinition.model_validate(graph_payload),
                )
            )
        latest = versions[-1].version if versions else 0
        return latest, versions

    def list(self) -> list[WorkflowRecord]:
        records: list[WorkflowRecord] = []

        with self._engine.connect() as conn:
            workflows = list(
                conn.execute(
                    sa.select(
                        WorkflowRow.workflow_id,
                        WorkflowRow.created_at,
                        WorkflowRow.updated_at,
                    ).order_by(WorkflowRow.updated_at.desc())
                ).all()
            )

            for wf in workflows:
                latest_row = conn.execute(
                    sa.select(
                        WorkflowVersionRow.version,
                        WorkflowVersionRow.created_at,
                        WorkflowVersionRow.graph,
                    )
                    .where(WorkflowVersionRow.workflow_id == wf.workflow_id)
                    .order_by(WorkflowVersionRow.version.desc())
                    .limit(1)
                ).one_or_none()

                versions: list[WorkflowVersion] = []
                if latest_row is not None:
                    graph_payload = _normalize_graph_json(latest_row.graph)
                    versions = [
                        WorkflowVersion(
                            version=latest_row.version,
                            created_at=latest_row.created_at,
                            graph=GraphDefinition.model_validate(graph_payload),
                        )
                    ]

                records.append(
                    WorkflowRecord(
                        workflow_id=wf.workflow_id,
                        created_at=wf.created_at,
                        updated_at=wf.updated_at,
                        versions=versions,
                    )
                )

        return records


def _default_store() -> WorkflowStore:
    if database_url():
        return PostgresWorkflowStore()
    return InMemoryWorkflowStore()


WORKFLOW_STORE: WorkflowStore = _default_store()
