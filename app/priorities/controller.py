# priorities/controller.py
from fastapi import APIRouter, status, Depends
from typing import List
from uuid import UUID

from ..auth.models import AuthContext
from ..database.core.database import DbSession
from . import models
from . import service
from app.auth.dependencies import get_auth_context;

router = APIRouter(
    prefix="/priorities",
    tags=["Priorities"]
)

@router.post("/", response_model=models.PriorityResponse, status_code=status.HTTP_201_CREATED)
def create(db: DbSession, data: models.PriorityCreate, auth_context: AuthContext = Depends(get_auth_context)):
    return service.create_priority(db, data, user_id=auth_context.user_id)

@router.put("/{id}", response_model=models.PriorityResponse)
def update(db: DbSession, id: UUID, data: models.PriorityUpdate, auth_context: AuthContext = Depends(get_auth_context)):
    return service.update_priority (db, id, data, user_id=auth_context.user_id)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(db: DbSession, id: UUID, auth_context: AuthContext = Depends(get_auth_context)):
    service.delete_priority(db, id)

@router.get("/", response_model=List[models.PriorityResponse])
def get_all(db: DbSession, auth_context: AuthContext = Depends(get_auth_context)):
    return service.get_priorities(db)