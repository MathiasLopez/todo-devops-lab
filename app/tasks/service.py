from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.entities.board import Board
from . import models
from app.entities.task import Task
from uuid import UUID

def create_task(db: Session, task: models.TaskCreate, user_id: UUID, board_id: UUID) -> Task:
     board = get_board_by_id(db, board_id)
     new_task = Task(**task.model_dump(), created_by = user_id, modified_by=user_id, board_id=board.id)
     db.add(new_task)
     db.commit()
     db.refresh(new_task)
     return new_task

def get_task_by_id(db: Session, id:UUID) -> Task:
     task = db.get(Task, id)
     if not task:
          raise HTTPException(status_code=404, detail="Task not found")
     
     return task

def get_board_by_id(db: Session, id: UUID) -> Board:
     board = db.get(Board, id)
     if not board:
          raise HTTPException(status_code=404, detail="Board not found")
     
     return board

def get_tasks(db: Session, board_id: Optional[UUID] = None) -> list[models.TaskResponse]:
     query = db.query(Task)
    
     if board_id:
          query = query.filter(Task.board_id == board_id)
     
     tasks = query.all()
     return tasks

def update_task(db: Session, id: UUID, task_to_update: models.TaskUpdate, user_id: UUID) -> Task:
    task = get_task_by_id(db, id)
    update_model_fields(task, task_to_update)
    task.modified_by = user_id
    db.commit()
    db.refresh(task)

    return task

def complete_task(db: Session, id: UUID, user_id: UUID) -> Task:
     task = get_task_by_id(db, id)
     if task.is_completed:
          print("Task {id} is already completed")
          return task
     
     task.is_completed = True
     task.modified_by = user_id
     db.commit()
     db.refresh(task)
     return task

def delete_task(db: Session, id: UUID) -> None:
     task = get_task_by_id(db, id)
     db.delete(task)
     db.commit()

def update_model_fields(model, update_obj) -> None:
    """
    Update the model attributes according to the non None values of the Pydantic object.
    """
    for field, value in update_obj.model_dump(exclude_unset=True).items():
        setattr(model, field, value)