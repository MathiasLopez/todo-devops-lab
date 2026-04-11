# columns/service.py
from sqlalchemy.orm import Session, joinedload, selectinload, load_only
from fastapi import HTTPException
from uuid import UUID
from ..entities.boardColumn import BoardColumn
from ..entities.task import Task
from . import models
from ..utils import model_utils
from ..boards.access import check_user_permissions
from ..boards.permissions import PERM_BOARD_VIEW, PERM_BOARD_UPDATE

def create(db: Session, board_id: UUID, user_id: UUID, data: models.ColumnCreate) -> BoardColumn:
    ctx = check_user_permissions(db, board_id, user_id, required_permission=PERM_BOARD_UPDATE)

    column = BoardColumn(
        board_id=ctx.board.id,
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
    check_user_permissions(db, column.board.id, user_id, required_permission=PERM_BOARD_UPDATE)
    model_utils.update_model_fields(column, data)
    column.modified_by = user_id
    db.commit()
    db.refresh(column)

    return column

def delete(db: Session, column_id: UUID, user_id: UUID):
    column = get_by_id(db, column_id, user_id)
    check_user_permissions(db, column.board.id, user_id, required_permission=PERM_BOARD_UPDATE)
    db.delete(column)
    db.commit()

def get_columns_with_tasks(db, board_id: UUID, user_id: UUID):
    ctx = check_user_permissions(db, board_id, user_id, required_permission=PERM_BOARD_VIEW)

    # columns
    # └── tasks
    #     ├── tags
    #     └── priority
    columns = db.query(BoardColumn).filter(BoardColumn.board_id == ctx.board.id).all()

    if not columns:
        return []

    column_ids = [col.id for col in columns]

    tasks = (
        db.query(Task)
        .options(
            joinedload(Task.priority),
            joinedload(Task.tags),
            joinedload(Task.parent).load_only(Task.id, Task.title),
            selectinload(Task.subtasks).load_only(Task.id, Task.title, Task.parent_id),
        )
        .filter(Task.column_id.in_(column_ids))
        .all()
    )

    tasks_by_column: dict[UUID, list[Task]] = {}
    for task in tasks:
        tasks_by_column.setdefault(task.column_id, []).append(task)

    # Build response DTOs; all tasks in the column are listed (roots and subtasks alike).
    # Parent tasks carry their subtasks eagerly loaded so the client can render relationships.
    result: list[models.ColumnWithTaskResponse] = []
    for col in columns:
        result.append(
            models.ColumnWithTaskResponse(
                id=col.id,
                board_id=col.board_id,
                title=col.title,
                description=col.description,
                created_by=col.created_by,
                created_at=col.created_at,
                modified_by=col.modified_by,
                modified_at=col.modified_at,
                tasks=[models.TaskResponse.model_validate(task) for task in tasks_by_column.get(col.id, [])],
            )
        )

    return result

def get_by_id(db: Session, column_id:UUID, user_id: UUID):
    column = db.get(BoardColumn, column_id)
    if not column:
        raise HTTPException(status_code=404, detail="Board not found")
    
    check_user_permissions(db, column.board.id, user_id, required_permission=PERM_BOARD_VIEW)
    
    return column
    
