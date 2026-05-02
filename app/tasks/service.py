# tasks/service.py
import logging

from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload, selectinload, load_only

from ..entities.task import Task
from ..entities.boardColumn import BoardColumn
from ..entities.tag import Tag
from ..entities.priority import Priority
from . import models
from ..columns import service as columns_service
from ..attachments import storage
from uuid import UUID
from typing import Optional
from ..utils import model_utils
from ..boards.access import check_user_permissions
from ..boards.permissions import (
    PERM_BOARD_VIEW,
    PERM_TASK_CREATE,
    PERM_TASK_UPDATE,
    PERM_TASK_DELETE,
)

logger = logging.getLogger(__name__)

def create_task(db: Session, task: models.TaskCreate, user_id: UUID, column_id: UUID) -> Task:
    column = columns_service.get_by_id(db, column_id, user_id)
    check_user_permissions(db, column.board_id, user_id, required_permission=PERM_TASK_CREATE)

    priority = db.query(Priority).filter(Priority.id == task.priority_id).first()
    if not priority:
        raise HTTPException(status_code=404, detail="Priority not found")

    if task.parent_id is not None:
        parent_task = db.get(Task, task.parent_id)
        if not parent_task:
            raise HTTPException(status_code=404, detail="Parent task not found")
        if parent_task.column.board_id != column.board_id:
            raise HTTPException(status_code=400, detail="Parent task must belong to the same board")
        if parent_task.parent_id is not None:
            raise HTTPException(status_code=400, detail="Parent task already has a parent (max one level allowed)")

    tags = []
    if task.tags:
        tags = db.query(Tag).filter(Tag.id.in_(task.tags)).all()

        if len(tags) != len(task.tags):
            existing_ids = {str(t.id) for t in tags}
            missing = [
                str(tag_id)
                for tag_id in task.tags
                if str(tag_id) not in existing_ids
            ]
            raise HTTPException(status_code=404, detail={"Some tags do not exist": missing})

        for tag in tags:
            if tag.board_id != column.board_id:
                raise HTTPException(status_code=400, detail=f"Tag {tag.id} does not belong to board {column.board_id}")

    try:
        new_task = Task(
            title=task.title,
            description=task.description,
            assigned=task.assigned,
            priority_id=task.priority_id,
            column_id=column.id,
            parent_id=task.parent_id,
            created_by=user_id,
            modified_by=user_id,
        )

        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        if tags:
            new_task.tags = tags
            db.commit()
            db.refresh(new_task)

        return new_task

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")

def get_task_by_id(db: Session, id:UUID, user_id: UUID) -> Task:
    task = db.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
     
    check_user_permissions(db, task.column.board_id, user_id, required_permission=PERM_BOARD_VIEW)
     
    return task

def get_task_details(db: Session, id: UUID, user_id: UUID) -> Task:
    task = (
        db.query(Task)
        .options(
            joinedload(Task.priority),
            joinedload(Task.tags),
            joinedload(Task.parent).load_only(Task.id, Task.title),
            selectinload(Task.subtasks).load_only(Task.id, Task.title, Task.parent_id),
        )
        .filter(Task.id == id)
        .first()
    )

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    check_user_permissions(db, task.column.board_id, user_id, required_permission=PERM_BOARD_VIEW)

    return task

def update_task(db: Session, id: UUID, data: models.TaskUpdate, user_id: UUID) -> Task:
    task = get_task_by_id(db, id, user_id)
    check_user_permissions(db, task.column.board_id, user_id, required_permission=PERM_TASK_UPDATE)

    target_column = None
    if data.column_id is not None:
        target_column = columns_service.get_by_id(db, data.column_id, user_id)

        if target_column.board_id != task.column.board_id:
            raise HTTPException(status_code=400, detail="Cannot move task across boards")

    target_board_id = target_column.board_id if target_column else task.column.board_id

    if data.priority_id is not None:
        priority = db.query(Priority).filter(Priority.id == data.priority_id).first()
        if not priority:
            raise HTTPException(status_code=404, detail="Priority not found")

    if "parent_id" in data.model_dump(exclude_unset=True):
        if data.parent_id:
            if data.parent_id == task.id:
                raise HTTPException(status_code=400, detail="Task cannot be its own parent")

            parent_task = db.get(Task, data.parent_id)
            if not parent_task:
                raise HTTPException(status_code=404, detail="Parent task not found")

            if parent_task.column.board_id != target_board_id:
                raise HTTPException(status_code=400, detail="Parent task must belong to the same board")

            if parent_task.parent_id is not None:
                raise HTTPException(status_code=400, detail="Parent task already has a parent (max one level allowed)")

    if data.tags is not None:
        tags = db.query(Tag).filter(Tag.id.in_(data.tags)).all()

        if len(tags) != len(data.tags):
            existing_ids = {str(t.id) for t in tags}
            missing = [str(tag_id) for tag_id in data.tags if str(tag_id) not in existing_ids]
            raise HTTPException(
                status_code=404,
                detail={"message": "Some tags do not exist", "missing_ids": missing},
            )

        for tag in tags:
            if tag.board_id != task.column.board_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Tag {tag.id} does not belong to board {task.column.board_id}",
                )
    else:
        tags = None

    try:
        model_utils.update_model_fields(task, data, exclude={"tags", "parent_id"})
        if "parent_id" in data.model_dump(exclude_unset=True):
            task.parent_id = data.parent_id
        task.modified_by = user_id

        if tags is not None:
            task.tags = tags

        db.commit()
        db.refresh(task)
        return task

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating task: {str(e)}")


def delete_task(db: Session, id: UUID, user_id: UUID) -> None:
    task = get_task_by_id(db, id, user_id)
    check_user_permissions(db, task.column.board_id, user_id, required_permission=PERM_TASK_DELETE)

    minio_keys = [a.minio_key for a in task.attachments]

    db.delete(task)
    db.commit()

    for key in minio_keys:
        try:
            storage.delete_file(key)
        except Exception:
            logger.exception("Orphan MinIO file after task delete: key=%s", key)


def search_tasks(
    db: Session,
    board_id: UUID,
    user_id: UUID,
    q: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    only_root: bool = False,
):
    # validate access & board existence
    check_user_permissions(db, board_id, user_id, required_permission=PERM_BOARD_VIEW)

    query = (
        db.query(Task)
        .join(BoardColumn, Task.column_id == BoardColumn.id)
        .filter(BoardColumn.board_id == board_id)
        .options(load_only(Task.id, Task.title, Task.parent_id, Task.modified_at, Task.created_at))
    )

    term = None
    if q:
        term = q.strip()
        if not term:
            term = None

    if term:
        like_pattern = f"%{term}%"
        clauses = [
            Task.title.ilike(like_pattern),
        ]
        if _is_uuid(term):
            clauses.append(Task.id == UUID(term))

        query = query.filter(or_(*clauses))

    # parent filter
    if only_root:
        query = query.filter(Task.parent_id.is_(None))

    items = (
        query.order_by(Task.modified_at.desc(), Task.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return items


def _is_uuid(value: str) -> bool:
    try:
        UUID(str(value))
        return True
    except Exception:
        return False
