"""Add attachments table

Revision ID: c3d4e5f6a7b8
Revises: 8b6c2d5f9a4b
Create Date: 2026-04-10 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str], None] = "8b6c2d5f9a4b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "attachments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("task_id", sa.UUID(), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("minio_key", sa.String(), nullable=False),
        sa.Column("content_type", sa.String(), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_attachments_task_id", "attachments", ["task_id"])


def downgrade() -> None:
    op.drop_index("ix_attachments_task_id", table_name="attachments")
    op.drop_table("attachments")
