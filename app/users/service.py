# users/service.py
import os
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from ..auth.access import ensure_base_global_role
from ..auth.models import AuthContext
from ..entities.role import Role, RoleScope
from ..entities.rolePermission import RolePermission
from ..entities.userRole import UserRole
from ..roles.service import build_role_response
from .models import UserResponse, UserMeResponse
from ..utils.http_client import get_http_client
from uuid import UUID

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


async def get_current_user_with_role(db: Session, auth_context: AuthContext) -> UserMeResponse:
    all_users = await get_users(auth_context)
    user = next((u for u in all_users if u.id == auth_context.user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found in SSO")

    ensure_base_global_role(db, user.id)
    role = _get_global_role(db, user.id)
    role_info = build_role_response(role)

    return UserMeResponse(
        id=user.id,
        username=user.username,
        role=role_info
    )

def _get_global_role(db: Session, user_id: UUID) -> Role | None:
    """
    Returns the unique global role assigned to a user, or None if not assigned.
    """
    return (
        db.query(Role)
        .join(UserRole, UserRole.role_id == Role.id)
        .options(
            joinedload(Role.permissions).joinedload(RolePermission.permission)
        )
        .filter(
            UserRole.user_id == user_id,
            Role.scope == RoleScope.GLOBAL,
        )
        .one_or_none()
    )
