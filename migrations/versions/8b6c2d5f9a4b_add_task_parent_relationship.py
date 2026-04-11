"""Add parent_id to tasks

Revision ID: 8b6c2d5f9a4b
Revises: 0d7f1e2a9c3c
Create Date: 2026-05-07 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "8b6c2d5f9a4b"
down_revision: Union[str, Sequence[str], None] = "0d7f1e2a9c3c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tasks",
        sa.Column(
            "parent_id",
            sa.UUID(),
            sa.ForeignKey("tasks.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("tasks", "parent_id")
