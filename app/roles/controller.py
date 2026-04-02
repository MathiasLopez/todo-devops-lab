from fastapi import APIRouter, Depends
from typing import List

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
def get_roles(db: DbSession, auth_context: AuthContext = Depends(get_auth_context)):
    return service.list_roles(db, auth_context.user_id)
