# services/column_service.py
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from uuid import UUID

from ..entities.board import Board
from ..entities.boardUserPermission import BoardUserPermission
from ..entities.boardColumn import BoardColumn
from ..entities.task import Task
from ..boards import service as boardService
from . import models
from ..utils import model_utils

def create(db: Session, board_id: UUID, user_id: UUID, data: models.ColumnCreate) -> BoardColumn:
    board = boardService.get_by_id(db, board_id, user_id)

    column = BoardColumn(
        board_id=board.id,
        title=data.title,
        description=data.description,
        created_by=user_id,
        modified_by=user_id
    )

    db.add(column)
    db.commit()
    db.refresh(column)
    return column

def update(db: Session, id: UUID, user_id: UUID, data: models.ColumnUpdate):
    column = get_by_id(db, id, user_id)
    model_utils.update_model_fields(column, data)
    column.modified_by = user_id
    db.commit()
    db.refresh(column)

    return column

def delete(db: Session, column_id: UUID, user_id: UUID):
    column = get_by_id(db, column_id, user_id)
    db.delete(column)
    db.commit()

def get_columns_with_tasks(db, board_id: UUID, user_id: UUID):
    board = boardService.get_by_id(db, board_id, user_id)

    # columns
    # └── tasks
    #     ├── tags
    #     └── priority
    columns = (
        db.query(BoardColumn)
        .options(
            joinedload(BoardColumn.tasks)
                .joinedload(Task.priority),
            joinedload(BoardColumn.tasks)
                .joinedload(Task.tags)
        )
        .filter(BoardColumn.board_id == board.id)
        .all()
    )

    return columns

def get_by_id(db: Session, column_id:UUID, user_id: UUID):
    column = _get_by_id(db, column_id)
    
    ensure_user_can_access_column(db, column, user_id)
    
    return column

def _get_by_id(db: Session, column_id:UUID) -> Board:
    column = db.get(BoardColumn, column_id)
    if not column:
        raise HTTPException(status_code=404, detail="Board not found")

    return column

def ensure_user_can_access_column(db, column: BoardColumn, user_id: UUID):
    board = column.board
    if not board:
        raise HTTPException(status_code=500, detail="Column has no board reference")

    has_permission = db.query(BoardUserPermission).filter_by(
        board_id=board.id,
        user_id=user_id
    ).first()

    if not has_permission:
        raise HTTPException(status_code=403, detail="Column not shared with you")