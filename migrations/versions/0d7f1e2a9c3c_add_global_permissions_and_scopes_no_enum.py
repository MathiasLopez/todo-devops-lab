"""add global permissions and scopes without enums

Revision ID: 0d7f1e2a9c3c
Revises: 3e4c1a2b5d7f
Create Date: 2026-04-31 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0d7f1e2a9c3c"
down_revision: Union[str, Sequence[str], None] = "3e4c1a2b5d7f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "roles",
        sa.Column("scope", sa.String(length=20), nullable=False, server_default="board"),
    )
    op.create_check_constraint(
        "ck_roles_scope", "roles", "scope IN ('global','board')"
    )

    op.drop_constraint("roles_name_key", "roles", type_="unique")
    op.create_unique_constraint("uq_role_name_scope", "roles", ["name", "scope"])

    op.execute("UPDATE roles SET scope = 'board'")
    op.alter_column("roles", "scope", server_default=None)

    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("role_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=False),
        sa.Column("modified_at", sa.DateTime(), nullable=False),
        sa.Column("modified_by", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "role_id"),
        sa.UniqueConstraint("user_id", "role_id", name="uq_user_role"),
    )

    system_user_id = "00000000-0000-0000-0000-000000000000"

    op.execute(
        f"""
        INSERT INTO permissions (id, name, description, created_at, created_by, modified_at, modified_by)
        VALUES
            ('3fc28a16-61e6-4d6e-8850-0cc08971aac2'::uuid, 'board.create', NULL, CURRENT_TIMESTAMP, '{system_user_id}'::uuid, CURRENT_TIMESTAMP, '{system_user_id}'::uuid),
            ('e67de7ff-a776-4261-b6a8-02695cf51de5'::uuid, 'role.read', NULL, CURRENT_TIMESTAMP, '{system_user_id}'::uuid, CURRENT_TIMESTAMP, '{system_user_id}'::uuid),
            ('267d3713-46ae-4401-b7e9-8cbbfdc82660'::uuid, 'user.read', NULL, CURRENT_TIMESTAMP, '{system_user_id}'::uuid, CURRENT_TIMESTAMP, '{system_user_id}'::uuid)
        ON CONFLICT (id) DO NOTHING;
    """
    )

    op.execute(
        f"""
        INSERT INTO roles (id, name, description, level, scope, created_at, created_by, modified_at, modified_by)
        VALUES
            ('00000000-0000-0000-0000-000000000005'::uuid, 'admin', 'Global administrator', 1000, 'global', CURRENT_TIMESTAMP, '{system_user_id}'::uuid, CURRENT_TIMESTAMP, '{system_user_id}'::uuid),
            ('00000000-0000-0000-0000-000000000006'::uuid, 'user', 'Default global user', 10, 'global', CURRENT_TIMESTAMP, '{system_user_id}'::uuid, CURRENT_TIMESTAMP, '{system_user_id}'::uuid)
        ON CONFLICT (id) DO NOTHING;
    """
    )

    op.execute(
        f"""
        INSERT INTO role_permissions (role_id, permission_id, created_at, created_by, modified_at, modified_by)
        SELECT '00000000-0000-0000-0000-000000000005'::uuid, p.id, CURRENT_TIMESTAMP, '{system_user_id}'::uuid, CURRENT_TIMESTAMP, '{system_user_id}'::uuid
        FROM permissions p
        ON CONFLICT (role_id, permission_id) DO NOTHING;
    """
    )

    op.execute(
        f"""
        INSERT INTO role_permissions (role_id, permission_id, created_at, created_by, modified_at, modified_by)
        VALUES
            ('00000000-0000-0000-0000-000000000006'::uuid, '3fc28a16-61e6-4d6e-8850-0cc08971aac2'::uuid, CURRENT_TIMESTAMP, '{system_user_id}'::uuid, CURRENT_TIMESTAMP, '{system_user_id}'::uuid),
            ('00000000-0000-0000-0000-000000000006'::uuid, 'e67de7ff-a776-4261-b6a8-02695cf51de5'::uuid, CURRENT_TIMESTAMP, '{system_user_id}'::uuid, CURRENT_TIMESTAMP, '{system_user_id}'::uuid)
        ON CONFLICT (role_id, permission_id) DO NOTHING;
    """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM role_permissions
        WHERE role_id IN ('00000000-0000-0000-0000-000000000005'::uuid, '00000000-0000-0000-0000-000000000006'::uuid);
        """
    )

    op.execute(
        """
        DELETE FROM roles WHERE id IN ('00000000-0000-0000-0000-000000000005'::uuid, '00000000-0000-0000-0000-000000000006'::uuid);
        """
    )

    op.execute(
        """
        DELETE FROM permissions WHERE id IN (
            '3fc28a16-61e6-4d6e-8850-0cc08971aac2'::uuid,
            'e67de7ff-a776-4261-b6a8-02695cf51de5'::uuid,
            '267d3713-46ae-4401-b7e9-8cbbfdc82660'::uuid
        );
        """
    )

    op.drop_table("user_roles")

    op.drop_constraint("uq_role_name_scope", "roles", type_="unique")
    op.create_unique_constraint("roles_name_key", "roles", ["name"])

    op.drop_constraint("ck_roles_scope", "roles", type_="check")
    op.drop_column("roles", "scope")
