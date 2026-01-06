"""init workflows and workspaces

Revision ID: 0001
Revises:
Create Date: 2026-01-05

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension (safe if already installed)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "workflows",
        sa.Column("workflow_id", sa.String(length=36), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "workflow_versions",
        sa.Column("workflow_id", sa.String(length=36), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("graph", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("workflow_id", "version"),
        sa.ForeignKeyConstraint(["workflow_id"], ["workflows.workflow_id"], ondelete="CASCADE"),
    )

    op.create_index(
        "ix_workflow_versions_workflow_id_version",
        "workflow_versions",
        ["workflow_id", "version"],
        unique=True,
    )

    op.create_table(
        "workspaces",
        sa.Column("workspace_id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "workspace_versions",
        sa.Column("workspace_id", sa.String(length=36), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("state", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("workspace_id", "version"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.workspace_id"], ondelete="CASCADE"),
    )

    op.create_index(
        "ix_workspace_versions_workspace_id_version",
        "workspace_versions",
        ["workspace_id", "version"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_workspace_versions_workspace_id_version", table_name="workspace_versions")
    op.drop_table("workspace_versions")
    op.drop_table("workspaces")

    op.drop_index("ix_workflow_versions_workflow_id_version", table_name="workflow_versions")
    op.drop_table("workflow_versions")
    op.drop_table("workflows")
