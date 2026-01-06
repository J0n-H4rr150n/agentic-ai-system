"""Workspace storage.

A "workspace" is a UI-level document (containers, nodes positions, sizes, etc.)
that can be saved/loaded and versioned.

If `DATABASE_URL` is set, `WORKSPACE_STORE` will use Postgres; otherwise it
falls back to an in-memory store.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import threading
from typing import Protocol, runtime_checkable
from uuid import uuid4

import sqlalchemy as sa

from backend.db.engine import create_db_engine, database_url
from backend.db.models import WorkspaceRow, WorkspaceVersionRow


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class WorkspaceVersion:
    version: int
    created_at: datetime
    state: dict


@dataclass(slots=True)
class WorkspaceRecord:
    workspace_id: str
    name: str | None
    created_at: datetime
    updated_at: datetime
    versions: list[WorkspaceVersion]


@runtime_checkable
class WorkspaceStore(Protocol):
    def create(self, *, state: dict, name: str | None = None) -> str: ...

    def create_version(self, workspace_id: str, *, state: dict, name: str | None = None) -> int: ...

    def get(self, workspace_id: str, *, version: int | None = None) -> tuple[WorkspaceRecord, WorkspaceVersion]: ...

    def list_versions(self, workspace_id: str) -> tuple[int, list[WorkspaceVersion]]: ...

    def list(self) -> list[WorkspaceRecord]: ...


class InMemoryWorkspaceStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._workspaces: dict[str, WorkspaceRecord] = {}

    def create(self, *, state: dict, name: str | None = None) -> str:
        workspace_id = str(uuid4())
        now = _now_utc()
        record = WorkspaceRecord(
            workspace_id=workspace_id,
            name=name,
            created_at=now,
            updated_at=now,
            versions=[WorkspaceVersion(version=1, created_at=now, state=state)],
        )

        with self._lock:
            self._workspaces[workspace_id] = record

        return workspace_id

    def create_version(self, workspace_id: str, *, state: dict, name: str | None = None) -> int:
        now = _now_utc()

        with self._lock:
            record = self._workspaces.get(workspace_id)
            if record is None:
                raise KeyError(workspace_id)

            next_version = (record.versions[-1].version + 1) if record.versions else 1
            record.versions.append(WorkspaceVersion(version=next_version, created_at=now, state=state))
            if name is not None:
                record.name = name
            record.updated_at = now

        return next_version

    def get(self, workspace_id: str, *, version: int | None = None) -> tuple[WorkspaceRecord, WorkspaceVersion]:
        with self._lock:
            record = self._workspaces.get(workspace_id)

        if record is None:
            raise KeyError(workspace_id)
        if not record.versions:
            raise RuntimeError("workspace has no versions")

        if version is None:
            return record, record.versions[-1]

        found = next((v for v in record.versions if v.version == version), None)
        if found is None:
            raise KeyError(f"{workspace_id}:{version}")

        return record, found

    def list_versions(self, workspace_id: str) -> tuple[int, list[WorkspaceVersion]]:
        with self._lock:
            record = self._workspaces.get(workspace_id)

        if record is None:
            raise KeyError(workspace_id)

        latest = record.versions[-1].version if record.versions else 0
        return latest, list(record.versions)

    def list(self) -> list[WorkspaceRecord]:
        with self._lock:
            records = list(self._workspaces.values())

        records.sort(key=lambda r: r.updated_at, reverse=True)
        return records


class PostgresWorkspaceStore:
    def __init__(self) -> None:
        self._engine = create_db_engine()

    def create(self, *, state: dict, name: str | None = None) -> str:
        workspace_id = str(uuid4())
        now = _now_utc()

        with self._engine.begin() as conn:
            conn.execute(
                sa.insert(WorkspaceRow).values(
                    workspace_id=workspace_id,
                    name=name,
                    created_at=now,
                    updated_at=now,
                )
            )
            conn.execute(
                sa.insert(WorkspaceVersionRow).values(
                    workspace_id=workspace_id,
                    version=1,
                    created_at=now,
                    state=state,
                )
            )

        return workspace_id

    def create_version(self, workspace_id: str, *, state: dict, name: str | None = None) -> int:
        now = _now_utc()

        with self._engine.begin() as conn:
            exists = conn.execute(
                sa.select(sa.literal(True))
                .select_from(WorkspaceRow)
                .where(WorkspaceRow.workspace_id == workspace_id)
            ).scalar_one_or_none()
            if not exists:
                raise KeyError(workspace_id)

            latest = conn.execute(
                sa.select(sa.func.max(WorkspaceVersionRow.version)).where(WorkspaceVersionRow.workspace_id == workspace_id)
            ).scalar_one()
            next_version = int(latest or 0) + 1

            conn.execute(
                sa.insert(WorkspaceVersionRow).values(
                    workspace_id=workspace_id,
                    version=next_version,
                    created_at=now,
                    state=state,
                )
            )

            update_values: dict[str, object] = {"updated_at": now}
            if name is not None:
                update_values["name"] = name
            conn.execute(
                sa.update(WorkspaceRow).where(WorkspaceRow.workspace_id == workspace_id).values(**update_values)
            )

        return next_version

    def get(self, workspace_id: str, *, version: int | None = None) -> tuple[WorkspaceRecord, WorkspaceVersion]:
        with self._engine.connect() as conn:
            ws = conn.execute(
                sa.select(
                    WorkspaceRow.workspace_id,
                    WorkspaceRow.name,
                    WorkspaceRow.created_at,
                    WorkspaceRow.updated_at,
                ).where(WorkspaceRow.workspace_id == workspace_id)
            ).one_or_none()
            if ws is None:
                raise KeyError(workspace_id)

            if version is None:
                row = conn.execute(
                    sa.select(
                        WorkspaceVersionRow.version,
                        WorkspaceVersionRow.created_at,
                        WorkspaceVersionRow.state,
                    )
                    .where(WorkspaceVersionRow.workspace_id == workspace_id)
                    .order_by(WorkspaceVersionRow.version.desc())
                    .limit(1)
                ).one_or_none()
            else:
                row = conn.execute(
                    sa.select(
                        WorkspaceVersionRow.version,
                        WorkspaceVersionRow.created_at,
                        WorkspaceVersionRow.state,
                    )
                    .where(WorkspaceVersionRow.workspace_id == workspace_id)
                    .where(WorkspaceVersionRow.version == version)
                ).one_or_none()

            if row is None:
                if version is None:
                    raise RuntimeError("workspace has no versions")
                raise KeyError(f"{workspace_id}:{version}")

            selected = WorkspaceVersion(version=row.version, created_at=row.created_at, state=row.state)
            record = WorkspaceRecord(
                workspace_id=ws.workspace_id,
                name=ws.name,
                created_at=ws.created_at,
                updated_at=ws.updated_at,
                versions=[selected],
            )

        return record, selected

    def list_versions(self, workspace_id: str) -> tuple[int, list[WorkspaceVersion]]:
        with self._engine.connect() as conn:
            exists = conn.execute(
                sa.select(sa.literal(True)).select_from(WorkspaceRow).where(WorkspaceRow.workspace_id == workspace_id)
            ).scalar_one_or_none()
            if not exists:
                raise KeyError(workspace_id)

            rows = list(
                conn.execute(
                    sa.select(
                        WorkspaceVersionRow.version,
                        WorkspaceVersionRow.created_at,
                        WorkspaceVersionRow.state,
                    )
                    .where(WorkspaceVersionRow.workspace_id == workspace_id)
                    .order_by(WorkspaceVersionRow.version.asc())
                ).all()
            )

        versions = [WorkspaceVersion(version=r.version, created_at=r.created_at, state=r.state) for r in rows]
        latest = versions[-1].version if versions else 0
        return latest, versions

    def list(self) -> list[WorkspaceRecord]:
        with self._engine.connect() as conn:
            workspaces = list(
                conn.execute(
                    sa.select(
                        WorkspaceRow.workspace_id,
                        WorkspaceRow.name,
                        WorkspaceRow.created_at,
                        WorkspaceRow.updated_at,
                    ).order_by(WorkspaceRow.updated_at.desc())
                ).all()
            )

            latest_by_workspace: dict[str, WorkspaceVersion] = {}
            for ws in workspaces:
                latest_row = conn.execute(
                    sa.select(
                        WorkspaceVersionRow.version,
                        WorkspaceVersionRow.created_at,
                        WorkspaceVersionRow.state,
                    )
                    .where(WorkspaceVersionRow.workspace_id == ws.workspace_id)
                    .order_by(WorkspaceVersionRow.version.desc())
                    .limit(1)
                ).one_or_none()

                if latest_row is None:
                    continue
                latest_by_workspace[ws.workspace_id] = WorkspaceVersion(
                    version=latest_row.version,
                    created_at=latest_row.created_at,
                    state=latest_row.state,
                )

        records: list[WorkspaceRecord] = []
        for ws in workspaces:
            versions: list[WorkspaceVersion] = []
            latest = latest_by_workspace.get(ws.workspace_id)
            if latest is not None:
                versions = [latest]
            records.append(
                WorkspaceRecord(
                    workspace_id=ws.workspace_id,
                    name=ws.name,
                    created_at=ws.created_at,
                    updated_at=ws.updated_at,
                    versions=versions,
                )
            )

        return records


def _default_store() -> WorkspaceStore:
    if database_url():
        return PostgresWorkspaceStore()
    return InMemoryWorkspaceStore()


WORKSPACE_STORE: WorkspaceStore = _default_store()
