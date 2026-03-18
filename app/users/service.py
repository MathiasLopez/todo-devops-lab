# users/service.py
from ..auth.models import AuthContext
from .models import UserResponse, UserMeResponse
from ..utils.http_client import get_http_client
import os
from sqlalchemy.orm import Session
from uuid import UUID
from ..entities.board import Board
from ..entities.boardUserPermission import BoardUserPermission
from ..entities.role import Role
from ..entities.permission import Permission
from ..entities.rolePermission import RolePermission
from ..roles.models import RoleResponse, PermissionResponse

from ..boards.permissions import PERM_BOARD_VIEW
from ..boards.access import check_user_permissions

AUTH_URL = os.getenv("AUTH_URL")

async def get_users(auth_context: AuthContext) -> list[UserResponse]:
    """
    Call the /api/users endpoint of the authentication service (SSO) and return a list of users.
    """
    async with get_http_client() as client:
        response = await client.get(
            f"{AUTH_URL}/api/users",
            headers={"Authorization": f"Bearer {auth_context.token}"}
        )
        response.raise_for_status()
        data = response.json()
        return [UserResponse(**user) for user in data]


async def get_current_user_with_role(db: Session, board_id, auth_context: AuthContext) -> UserMeResponse:
    all_users = await get_users(auth_context)
    user = next((u for u in all_users if u.id == auth_context.user_id), None)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found in SSO")

    role_info = None

    if board_id:
        ctx = check_user_permissions(db, board_id, user.id, PERM_BOARD_VIEW)
        perms = [
            PermissionResponse(
                id=rp.permission.id,
                name=rp.permission.name,
                description=rp.permission.description,
            )
            for rp in ctx.role.permissions
        ]
        role_info = RoleResponse(
            id=ctx.role.id,
            name=ctx.role.name,
            description=ctx.role.description,
            level=ctx.role.level,
            permissions=perms,
        )

    return UserMeResponse(
        id=user.id,
        username=user.username,
        role=role_info
    )
     
