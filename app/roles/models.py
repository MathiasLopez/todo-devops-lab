from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel


class PermissionResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None

class RoleResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    scope: str
    level: int
    permissions: List[PermissionResponse]
