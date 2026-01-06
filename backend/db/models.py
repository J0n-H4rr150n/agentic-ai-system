from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.base import Base


class WorkflowRow(Base):
    __tablename__ = "workflows"

    workflow_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class WorkflowVersionRow(Base):
    __tablename__ = "workflow_versions"

    workflow_id: Mapped[str] = mapped_column(String(36), ForeignKey("workflows.workflow_id", ondelete="CASCADE"), primary_key=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    graph: Mapped[dict] = mapped_column(JSON, nullable=False)


class WorkspaceRow(Base):
    __tablename__ = "workspaces"

    workspace_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class WorkspaceVersionRow(Base):
    __tablename__ = "workspace_versions"

    workspace_id: Mapped[str] = mapped_column(String(36), ForeignKey("workspaces.workspace_id", ondelete="CASCADE"), primary_key=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    state: Mapped[dict] = mapped_column(JSON, nullable=False)
