"""Add name column to workflows table

Revision ID: 0002
Revises: 0001
Create Date: 2026-01-08

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade():
    # Add name column to workflows table
    op.add_column('workflows', sa.Column('name', sa.String(200), nullable=True))


def downgrade():
    # Remove name column from workflows table
    op.drop_column('workflows', 'name')
