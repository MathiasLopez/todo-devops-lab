from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..entities.boardUserPermission import BoardUserPermission
from . import models
from ..entities.task import Task
from ..boards.service import get_by_id as get_board_by_id
from uuid import UUID

def create_task(db: Session, task: models.TaskCreate, user_id: UUID, board_id: UUID) -> Task:
     board = get_board_by_id(db, board_id, user_id=user_id)
     new_task = Task(**task.model_dump(), created_by = user_id, modified_by=user_id, board_id=board.id)
     db.add(new_task)
     db.commit()
     db.refresh(new_task)
     return new_task

def get_task_by_id(db: Session, id:UUID, user_id: UUID) -> Task:
     task = db.get(Task, id)
     if not task:
          raise HTTPException(status_code=404, detail="Task not found")
     
     has_permission = db.query(BoardUserPermission).filter_by(
        board_id=task.board_id,
        user_id=user_id
    ).first()
     
     if not has_permission:
        raise HTTPException(status_code=403, detail="Board not shared with you")
     
     return task

def get_tasks(db: Session, user_id: UUID, board_id: UUID) -> list[models.TaskResponse]:
     has_access = (
          db.query(BoardUserPermission)
          .filter(
               BoardUserPermission.board_id == board_id,
               BoardUserPermission.user_id == user_id,
          )
          .first()
     )
     
     if not has_access:
          raise HTTPException(status_code=403, detail="Board not shared with you")
     
     query = db.query(Task).filter(Task.board_id == board_id)

     tasks = query.all()

     return tasks

def update_task(db: Session, id: UUID, task_to_update: models.TaskUpdate, user_id: UUID) -> Task:
    task = get_task_by_id(db, id, user_id)
    update_model_fields(task, task_to_update)
    task.modified_by = user_id
    db.commit()
    db.refresh(task)

    return task

def complete_task(db: Session, id: UUID, user_id: UUID) -> Task:
     task = get_task_by_id(db, id, user_id)
     if task.is_completed:
          return task
     
     task.is_completed = True
     task.modified_by = user_id
     db.commit()
     db.refresh(task)
     return task

def delete_task(db: Session, id: UUID, user_id: UUID) -> None:
     task = get_task_by_id(db, id, user_id)
     db.delete(task)
     db.commit()

def update_model_fields(model, update_obj) -> None:
    """
    Update the model attributes according to the non None values of the Pydantic object.
    """
    for field, value in update_obj.model_dump(exclude_unset=True).items():
        setattr(model, field, value)