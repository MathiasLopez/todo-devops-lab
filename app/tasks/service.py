from fastapi import HTTPException
from sqlalchemy.orm import Session
from . import models
from app.entities.task import Task
from uuid import UUID

def create_task(db: Session, task: models.TaskCreate, user_id: UUID) -> Task:
        new_task = Task(**task.model_dump(), created_by = user_id)
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return new_task

def get_task_by_id(db: Session, id:UUID) -> Task:
    task = db.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task

def get_tasks(db: Session) -> list[models.TaskResponse]:
     tasks = db.query(Task).all()

     return tasks

def update_task(db: Session, id: UUID, task_to_update: models.TaskCreate) -> Task:
    task_data = task_to_update.model_dump(exclude_unset=True)
    db.query(Task).filter(Task.id == id).update(task_data)
    db.commit()

    return get_task_by_id(db, id)

def complete_task(db: Session, id: UUID) -> Task:
     task = get_task_by_id(db, id)
     if task.is_completed:
          print("Task {id} is already completed")
          return task
     
     task.is_completed = True
     db.commit()
     db.refresh(task)
     return task

def delete_task(db: Session, id: UUID) -> None:
     task = get_task_by_id(db, id)
     db.delete(task)
     db.commit()