from fastapi import APIRouter, status, Depends
from typing import List
from uuid import UUID
from ..auth.models import AuthContext
from ..database.core.database import DbSession
from . import models
from . import service
from app.auth.dependencies import get_auth_context;

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

@router.put("/{id}", response_model=models.TaskResponse)
def update_task(db: DbSession, id: UUID, task_to_update: models.TaskUpdate, auth_context: AuthContext = Depends(get_auth_context)):
    return service.update_task(db, id, task_to_update, auth_context.user_id)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(db: DbSession, id: UUID, auth_context: AuthContext = Depends(get_auth_context)):
    service.delete_task(db, id, auth_context.user_id)