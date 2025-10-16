from fastapi import APIRouter, Depends
from typing import List
from ..auth.models import AuthContext
from . import models
from . import service

from ..auth.dependencies import get_auth_context;

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/", response_model=List[models.User])
async def get_users(auth_context: AuthContext = Depends(get_auth_context)):
    return await service.get_users(auth_context)