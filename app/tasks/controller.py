from fastapi import APIRouter, status, Depends
from typing import List
from uuid import UUID
from ..auth.models import AuthContext
from ..database.core import DbSession
from . import models
from . import service
from app.auth.dependencies import get_auth_context;

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

# @router.get("/{id}", response_model=models.TaskResponse)
# def get_task(db: DbSession, id: UUID, auth_context: AuthContext = Depends(get_auth_context)):
#     return service.get_task_by_id(db, id)

# @router.get("/", response_model=List[models.TaskResponse])
# def get_tasks(db: DbSession, auth_context: AuthContext = Depends(get_auth_context)):
#     return service.get_tasks(db)

@router.put("/{id}", response_model=models.TaskResponse)
def update_task(db: DbSession, id: UUID, task_to_update: models.TaskUpdate, auth_context: AuthContext = Depends(get_auth_context)):
    return service.update_task(db, id, task_to_update, auth_context.user_id)

@router.put("/{id}/complete", response_model=models.TaskResponse)
def complete_task(db: DbSession, id: UUID, auth_context: AuthContext = Depends(get_auth_context)):
    return service.complete_task(db, id, auth_context.user_id)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(db: DbSession, id: UUID, auth_context: AuthContext = Depends(get_auth_context)):
    service.delete_task(db, id, auth_context.user_id)