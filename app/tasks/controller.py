# tasks/controller.py
from fastapi import APIRouter, status, Depends, Query
from typing import List, Optional
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

@router.get("/search", response_model=list[models.TaskSearchItem])
def search_tasks(
    db: DbSession,
    board_id: UUID = Query(..., alias="boardId"),
    q: Optional[str] = Query(None),
    limit: int = Query(20, gt=0, le=100),
    offset: int = Query(0, ge=0),
    only_root: bool = Query(False, alias="onlyRoot"),
    auth_context: AuthContext = Depends(get_auth_context),
):
    return service.search_tasks(db, board_id, auth_context.user_id, q, limit, offset, only_root=only_root)

@router.get("/{id}", response_model=models.TaskResponse)
def get_task(db: DbSession, id: UUID, auth_context: AuthContext = Depends(get_auth_context)):
    return service.get_task_details(db, id, auth_context.user_id)

@router.put("/{id}", response_model=models.TaskResponse)
def update_task(db: DbSession, id: UUID, task_to_update: models.TaskUpdate, auth_context: AuthContext = Depends(get_auth_context)):
    return service.update_task(db, id, task_to_update, auth_context.user_id)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(db: DbSession, id: UUID, auth_context: AuthContext = Depends(get_auth_context)):
    service.delete_task(db, id, auth_context.user_id)
