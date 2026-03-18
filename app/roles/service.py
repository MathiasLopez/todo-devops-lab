from sqlalchemy.orm import Session, joinedload

from ..entities.role import Role
from ..entities.rolePermission import RolePermission
from .models import RoleResponse, PermissionResponse
from ..boards.permissions import PERM_BOARD_VIEW
from ..boards.access import check_user_permissions


def list_roles(db: Session, board_id, user_id) -> list[RoleResponse]:
    check_user_permissions(db, board_id, user_id, required_permission=PERM_BOARD_VIEW)
    roles = (
        db.query(Role)
        .options(
            joinedload(Role.permissions).joinedload(RolePermission.permission)
        )
        .all()
    )

    result: list[RoleResponse] = []
    for role in roles:
        permissions = [
            PermissionResponse(
                id=rp.permission.id,
                name=rp.permission.name,
                description=rp.permission.description,
            )
            for rp in role.permissions
        ]
        result.append(
            RoleResponse(
                id=role.id,
                name=role.name,
                description=role.description,
                level=role.level,
                permissions=permissions,
            )
        )
    return result
