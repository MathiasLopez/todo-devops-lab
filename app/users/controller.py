# users/controller.py
from fastapi import APIRouter, Depends
from typing import List, Optional
from ..auth.models import AuthContext
from . import models
from . import service
from ..database.core.database import DbSession

from ..auth.dependencies import get_auth_context;

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/", response_model=List[models.UserResponse])
async def get_users(auth_context: AuthContext = Depends(get_auth_context)):
    return await service.get_users(auth_context)


@router.get("/me", response_model=models.UserMeResponse)
async def get_me(db: DbSession, auth_context: AuthContext = Depends(get_auth_context), board_id: Optional[str] = None):
    return await service.get_current_user_with_role(db, board_id, auth_context)
