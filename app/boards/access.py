from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..entities.board import Board
from ..entities.boardUserPermission import BoardUserPermission
from ..entities.role import Role
from ..entities.permission import Permission
from ..entities.rolePermission import RolePermission
from sqlalchemy.orm import joinedload
from .permissions import PermissionContext


def check_user_permissions(
    db: Session,
    board_id,
    user_id,
    required_permission: str,
) -> PermissionContext:
    """
    Checks whether a user has access to a board and a specific permission.
    Returns PermissionContext(board, role) or raises HTTP errors.
    """
    board = db.get(Board, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    membership = (
        db.query(BoardUserPermission)
        .join(Role, Role.id == BoardUserPermission.role_id)
        .filter(BoardUserPermission.board_id == board_id, BoardUserPermission.user_id == user_id)
        .first()
    )

    if not membership:
        raise HTTPException(status_code=403, detail="Board not shared with you")

    role = (
        db.query(Role)
        .options(joinedload(Role.permissions).joinedload(RolePermission.permission))
        .filter(Role.id == membership.role_id)
        .one()
    )

    has_permission = any(
        rp.permission.name == required_permission
        for rp in role.permissions
    )
    if not has_permission:
        raise HTTPException(status_code=403, detail="You do not have permission to perform this action")

    return PermissionContext(board=board, role=role)
