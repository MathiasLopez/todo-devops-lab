# tasks/service.py
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..entities.task import Task
from ..entities.tag import Tag
from ..entities.priority import Priority
from . import models
from ..columns import service as columns_service
from uuid import UUID
from ..utils import model_utils
from ..boards.service import check_user_permissions

def create_task(db: Session, task: models.TaskCreate, user_id: UUID, column_id: UUID) -> Task:
    column = columns_service.get_by_id(db, column_id, user_id)

    priority = db.query(Priority).filter(Priority.id == task.priority_id).first()
    if not priority:
        raise HTTPException(status_code=404, detail="Priority not found")

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
     
     check_user_permissions(db, task.column.board_id, user_id)
     
     return task

def update_task(db: Session, id: UUID, data: models.TaskUpdate, user_id: UUID) -> Task:
    task = get_task_by_id(db, id, user_id)
    
    if data.priority_id is not None:
        priority = db.query(Priority).filter(Priority.id == data.priority_id).first()
        
        if not priority:
            raise HTTPException(status_code=404, detail="Priority not found")
        
    tags = None
    if data.tags is not None:
        tags = db.query(Tag).filter(Tag.id.in_(data.tags)).all()
        
        if len(tags) != len(data.tags):
            existing_ids = {str(t.id) for t in tags}
            missing = [
                str(tag_id)
                for tag_id in data.tags
                if str(tag_id) not in existing_ids
                ]
            raise HTTPException(status_code=404, detail={"Some tags do not exist": missing})
        for tag in tags:
            if tag.board_id != task.column.board_id:
                raise HTTPException(status_code=400, detail=f"Tag {tag.id} does not belong to board {task.column.board_id}")
    
    try:
        model_utils.update_model_fields(task, data, exclude={"tags"})
        task.modified_by = user_id

        if data.tags is not None:
            task.tags = tags

        db.commit()
        db.refresh(task)
        return task

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating task: {str(e)}")


def delete_task(db: Session, id: UUID, user_id: UUID) -> None:
     task = get_task_by_id(db, id, user_id)
     db.delete(task)
     db.commit()