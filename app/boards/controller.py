from fastapi import APIRouter, status, Depends
from typing import List
from uuid import UUID

from ..auth.models import AuthContext
from ..database.core.database import DbSession
from . import model
from . import service
from app.auth.dependencies import get_auth_context;
from ..columns.models import ColumnCreate, ColumnResponse, ColumnWithTaskResponse
from ..columns import service as column_services
from ..tasks.models import TaskCreate, TaskResponse
from ..tasks.service import create_task as create_task_service
from ..tasks.service import get_tasks as get_task_service
from ..tags.models import TagCreate, TagResponse
from ..tags import service as tag_services

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
    service.delete(db, id, auth_context.user_id)

@router.get("/", response_model=List[model.BoardResponse])
def get_Boards(db: DbSession, auth_context: AuthContext = Depends(get_auth_context)):
    return service.get_all(db, user_id=auth_context.user_id)

@router.get("/{id}", response_model=model.BoardResponse)
def get_board(db: DbSession, id: UUID, auth_context: AuthContext = Depends(get_auth_context)):
    return service.get_by_id(db, id, auth_context.user_id)

# Columns
@router.post("/{board_id}/columns", response_model=ColumnResponse)
def create_column(db: DbSession, board_id: UUID, data: ColumnCreate, auth_context: AuthContext = Depends(get_auth_context)):
    return column_services.create(db, board_id, auth_context.user_id, data)

@router.get("/{board_id}/columns", response_model=list[ColumnWithTaskResponse])
def get_columns(db: DbSession, board_id: UUID, auth_context: AuthContext = Depends(get_auth_context)):
    return column_services.get_columns_with_tasks(db, board_id, auth_context.user_id)


# Tasks
@router.post("/{board_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(db: DbSession, board_id: UUID, task: TaskCreate, auth_context: AuthContext = Depends(get_auth_context)):
    return create_task_service(db, task, user_id=auth_context.user_id, board_id=board_id)

@router.get("/{board_id}/tasks",response_model=List[TaskResponse])
def get_tasks(db: DbSession, board_id: UUID, auth_context: AuthContext = Depends(get_auth_context)):
    return get_task_service(db, user_id=auth_context.user_id, board_id=board_id)

# Tags
@router.post("/{board_id}/tags", response_model=TagResponse)
def create_tag(db: DbSession, board_id: UUID, data: TagCreate, auth_context: AuthContext = Depends(get_auth_context)):
    return tag_services.create_tag(db, data, auth_context.user_id, board_id)

@router.get("/{board_id}/tags", response_model=list[TagResponse])
def get_tags(db: DbSession, board_id: UUID, auth_context: AuthContext = Depends(get_auth_context)):
    return tag_services.get_tags(db, board_id, auth_context.user_id)