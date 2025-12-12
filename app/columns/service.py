# columns/service.py
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from uuid import UUID
from ..entities.boardColumn import BoardColumn
from ..entities.task import Task
from ..boards import service as boardService
from . import models
from ..utils import model_utils
from ..boards.service import check_user_permissions

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

def update(db: Session, column_id: UUID, user_id: UUID, data: models.ColumnUpdate):
    column = get_by_id(db, column_id, user_id)
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
    column = db.get(BoardColumn, column_id)
    if not column:
        raise HTTPException(status_code=404, detail="Board not found")
    
    check_user_permissions(db, column.board.id, user_id)
    
    return column
    