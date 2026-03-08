"""add role level

Revision ID: c7c3a1e4b8a1
Revises: f7853127aa6d
Create Date: 2026-03-05 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7c3a1e4b8a1'
down_revision: Union[str, Sequence[str], None] = 'f7853127aa6d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('roles', sa.Column('level', sa.Integer(), nullable=False, server_default='0'))

    op.execute(
        """
        UPDATE roles SET level = CASE name
            WHEN 'owner' THEN 100
            WHEN 'admin' THEN 70
            WHEN 'member' THEN 40
            WHEN 'viewer' THEN 10
            ELSE 0
        END;
        """
    )

    op.alter_column('roles', 'level', server_default=None)


def downgrade() -> None:
    op.drop_column('roles', 'level')
