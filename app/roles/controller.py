from fastapi import APIRouter, Depends
from typing import List
from uuid import UUID

from ..database.core.database import DbSession
from . import service
from .models import RoleResponse
from ..auth.models import AuthContext
from ..auth.dependencies import get_auth_context

router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
)


@router.get("/", response_model=List[RoleResponse])
def get_roles(db: DbSession, board_id: UUID, auth_context: AuthContext = Depends(get_auth_context)):
    return service.list_roles(db, board_id, auth_context.user_id)
