from sqlalchemy.orm import Session, joinedload

from ..entities.role import Role
from ..entities.rolePermission import RolePermission
from .models import RoleResponse, PermissionResponse
from app.auth.access import require_global_permission
from app.auth.permissions import PERM_ROLE_READ


def list_roles(db: Session, user_id) -> list[RoleResponse]:
    require_global_permission(db, user_id, PERM_ROLE_READ)
    roles = (
        db.query(Role)
        .options(
            joinedload(Role.permissions).joinedload(RolePermission.permission)
        )
        .all()
    )

    return [build_role_response(role) for role in roles]


def build_role_response(role: Role) -> RoleResponse:
    permissions = [
        PermissionResponse(
            id=rp.permission.id,
            name=rp.permission.name,
            description=rp.permission.description,
        )
        for rp in role.permissions
    ]
    return RoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        scope=role.scope,
        level=role.level,
        permissions=permissions,
    )
