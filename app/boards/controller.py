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
from ..tags.models import TagCreate, TagResponse
from ..tags import service as tag_services
from ..users import models as user_models

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

# Board users
@router.get("/{board_id}/users", response_model=List[user_models.UserResponse])
async def get_board_users(db: DbSession, board_id: UUID, auth_context: AuthContext = Depends(get_auth_context)):
    return await service.get_board_users(db, board_id, auth_context)

# Board members management
@router.post("/{board_id}/members", response_model=model.BoardMemberResponse, status_code=status.HTTP_201_CREATED)
def add_board_member(db: DbSession, board_id: UUID, payload: model.BoardMemberCreate, auth_context: AuthContext = Depends(get_auth_context)):
    return service.add_board_member(db, board_id, payload, auth_context.user_id)

@router.patch("/{board_id}/members/{user_id}", response_model=model.BoardMemberResponse)
def update_board_member(db: DbSession, board_id: UUID, user_id: UUID, payload: model.BoardMemberUpdate, auth_context: AuthContext = Depends(get_auth_context)):
    return service.update_board_member(db, board_id, user_id, payload, auth_context.user_id)

@router.delete("/{board_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_board_member(db: DbSession, board_id: UUID, user_id: UUID, auth_context: AuthContext = Depends(get_auth_context)):
    service.delete_board_member(db, board_id, user_id, auth_context.user_id)

# Columns
@router.post("/{board_id}/columns", response_model=ColumnResponse, status_code=status.HTTP_201_CREATED)
def create_column(db: DbSession, board_id: UUID, data: ColumnCreate, auth_context: AuthContext = Depends(get_auth_context)):
    return column_services.create(db, board_id, auth_context.user_id, data)

@router.get("/{board_id}/columns", response_model=list[ColumnWithTaskResponse])
def get_columns_with_tasks(db: DbSession, board_id: UUID, auth_context: AuthContext = Depends(get_auth_context)):
    return column_services.get_columns_with_tasks(db, board_id, auth_context.user_id)

# Tags
@router.post("/{board_id}/tags", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(db: DbSession, board_id: UUID, data: TagCreate, auth_context: AuthContext = Depends(get_auth_context)):
    return tag_services.create_tag(db, data, auth_context.user_id, board_id)

@router.get("/{board_id}/tags", response_model=list[TagResponse])
def get_tags(db: DbSession, board_id: UUID, auth_context: AuthContext = Depends(get_auth_context)):
    return tag_services.get_tags(db, board_id, auth_context.user_id)
