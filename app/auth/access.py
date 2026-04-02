from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.entities.permission import Permission
from app.entities.role import Role, RoleScope
from app.entities.rolePermission import RolePermission
from app.entities.userRole import UserRole

SYSTEM_USER_ID = UUID("00000000-0000-0000-0000-000000000000")


def ensure_base_global_role(db: Session, user_id: UUID) -> None:
    """
    Ensure every authenticated user has at least the base global role ("user").
    This avoids blocking first actions (e.g., creating the first board) when the
    user does not yet have an entry in user_roles.
    """
    existing = db.query(UserRole).filter_by(user_id=user_id).first()
    if existing:
        return

    base_role = (
        db.query(Role)
        .filter(Role.name == "user", Role.scope == RoleScope.GLOBAL)
        .one_or_none()
    )
    if not base_role:
        # Fail loudly so seed data issues surface early.
        raise HTTPException(status_code=500, detail="Base global role is not configured")

    now = datetime.now(timezone.utc)
    db.add(
        UserRole(
            user_id=user_id,
            role_id=base_role.id,
            created_at=now,
            created_by=SYSTEM_USER_ID,
            modified_at=now,
            modified_by=SYSTEM_USER_ID,
        )
    )
    db.flush()
    db.commit()


def find_global_role_with_permission(
    db: Session,
    user_id: UUID,
    permission_name: str,
) -> Optional[Role]:
    """
    Returns a global Role that grants the requested permission, or None.
    """
    return (
        db.query(Role)
        .join(UserRole, UserRole.role_id == Role.id)
        .join(RolePermission, RolePermission.role_id == Role.id)
        .join(Permission, Permission.id == RolePermission.permission_id)
        .options(joinedload(Role.permissions).joinedload(RolePermission.permission))
        .filter(
            UserRole.user_id == user_id,
            Role.scope == RoleScope.GLOBAL,
            Permission.name == permission_name,
        )
        .first()
    )


def require_global_permission(db: Session, user_id: UUID, permission_name: str) -> Role:
    """
    Ensure the user has the specified global permission.
    """
    ensure_base_global_role(db, user_id)
    role = find_global_role_with_permission(db, user_id, permission_name)
    if not role:
        raise HTTPException(status_code=403, detail="You do not have permission to perform this action")
    return role
