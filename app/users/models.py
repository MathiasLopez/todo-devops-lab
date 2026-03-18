# users/models.py
from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from ..roles.models import RoleResponse


class UserResponse(BaseModel):
    id: UUID
    username: str


class UserMeResponse(UserResponse):
    role: Optional[RoleResponse] = None
