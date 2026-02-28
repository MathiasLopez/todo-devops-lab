"""Make board column descriptions nullable

Revision ID: 2a8a26c5bfa5
Revises: 9d0e2a8650b8
Create Date: 2026-02-28 07:30:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "2a8a26c5bfa5"
down_revision = "9d0e2a8650b8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "board_columns",
        "description",
        existing_type=sa.String(),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "board_columns",
        "description",
        existing_type=sa.String(),
        nullable=False,
    )
