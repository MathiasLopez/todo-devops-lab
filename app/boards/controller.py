from fastapi import APIRouter, status, Depends
from typing import List
from uuid import UUID
from ..auth.models import AuthContext
from ..database.core import DbSession
from . import model
from . import service
from app.auth.dependencies import get_auth_context;
from ..tasks.models import TaskCreate, TaskResponse
from ..tasks.service import create_task as create_task_service
from ..tasks.service import get_tasks as get_task_service

router = APIRouter(
    prefix="/boards",
    tags=["Boards"]
)

@router.post("/", response_model=model.BoardResponse, status_code=status.HTTP_201_CREATED)
def create(db: DbSession, board: model.BoardCreate, auth_context: AuthContext = Depends(get_auth_context)):
    return service.create(db, board, user_id=auth_context.user_id)

@router.put("/{id}", response_model=model.BoardResponse)
def update_Board(db: DbSession, id: UUID, board: model.BoardUpdate, auth_context: AuthContext = Depends(get_auth_context)):
    return service.update(db, id, board, user_id=auth_context.user_id)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_Board(db: DbSession, id: UUID, auth_context: AuthContext = Depends(get_auth_context)):
    service.delete(db, id)

@router.get("/", response_model=List[model.BoardResponse])
def get_Boards(db: DbSession, auth_context: AuthContext = Depends(get_auth_context)):
    return service.get_all(db)

@router.get("/{id}", response_model=model.BoardResponse)
def get_board(db: DbSession, id: UUID, auth_context: AuthContext = Depends(get_auth_context)):
    return service.get_by_id(db, id)

# Tasks
@router.post("/{board_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(db: DbSession, board_id: UUID, task: TaskCreate, auth_context: AuthContext = Depends(get_auth_context)):
    return create_task_service(db, task, user_id=auth_context.user_id, board_id=board_id)

@router.get("/{board_id}/tasks",response_model=List[TaskResponse])
def get_tasks(db: DbSession, board_id: UUID, auth_context: AuthContext = Depends(get_auth_context)):
    return get_task_service(db, board_id=board_id)