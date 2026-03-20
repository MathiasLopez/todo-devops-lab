"""Add color to priorities and seed system priorities

Revision ID: 1b2cf4d1c0f5
Revises: c7c3a1e4b8a1
Create Date: 2026-03-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1b2cf4d1c0f5"
down_revision: Union[str, Sequence[str], None] = "c7c3a1e4b8a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


SYSTEM_USER_ID = "00000000-0000-0000-0000-000000000000"
SYSTEM_PRIORITIES = [
    ("00000000-0000-0000-0000-00000000000a", "Low", "#22C55E"),
    ("00000000-0000-0000-0000-00000000000b", "Medium", "#EAB308"),
    ("00000000-0000-0000-0000-00000000000c", "High", "#EF4444"),
]


def upgrade() -> None:
    op.add_column(
        "priorities",
        sa.Column(
            "color",
            sa.String(length=7),
            nullable=True,  # allow existing rows
        ),
    )

    # Backfill existing priorities with a neutral gray
    op.execute("UPDATE priorities SET color = '#9CA3AF' WHERE color IS NULL")

    op.create_check_constraint(
        "ck_priorities_color_hex",
        "priorities",
        "color ~* '^#[0-9A-F]{6}$'",
    )

    # Enforce NOT NULL after backfill + constraint
    op.alter_column("priorities", "color", nullable=False)

    for priority_id, title, color in SYSTEM_PRIORITIES:
        op.execute(
            f"""
            INSERT INTO priorities (id, title, color, created_at, created_by, modified_at, modified_by)
            VALUES (
                '{priority_id}'::uuid,
                '{title}',
                '{color}',
                CURRENT_TIMESTAMP,
                '{SYSTEM_USER_ID}'::uuid,
                CURRENT_TIMESTAMP,
                '{SYSTEM_USER_ID}'::uuid
            )
            ON CONFLICT (id) DO NOTHING;
            """
        )


def downgrade() -> None:
    op.execute(
        f"""
        DELETE FROM priorities
        WHERE id IN ({','.join(f"'{pid}'::uuid" for pid, _, _ in SYSTEM_PRIORITIES)})
        """
    )
    op.drop_constraint("ck_priorities_color_hex", "priorities")
    op.drop_column("priorities", "color")
