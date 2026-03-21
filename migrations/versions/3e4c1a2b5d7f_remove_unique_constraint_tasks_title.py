"""Remove unique constraint on tasks.title

Revision ID: 3e4c1a2b5d7f
Revises: 1b2cf4d1c0f5
Create Date: 2026-03-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3e4c1a2b5d7f"
down_revision: Union[str, Sequence[str], None] = "1b2cf4d1c0f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop possible unique constraint/index on tasks.title (safe if not present)
    op.execute("ALTER TABLE tasks DROP CONSTRAINT IF EXISTS tasks_title_key;")
    op.execute("DROP INDEX IF EXISTS tasks_title_key;")
    op.execute("DROP INDEX IF EXISTS uq_tasks_title;")
    op.execute("DROP INDEX IF EXISTS tasks_title_idx;")


def downgrade() -> None:
    # Recreate unique constraint if needed on downgrade
    op.execute("ALTER TABLE tasks ADD CONSTRAINT tasks_title_key UNIQUE (title);")
