# priorities/service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID

from ..utils import model_utils
from ..entities.priority import Priority
from .models import PriorityCreate, PriorityUpdate

def create_priority(db: Session, data: PriorityCreate, user_id: UUID) -> Priority:
    new_priority = Priority(**data.model_dump(), created_by = user_id, modified_by=user_id)
    db.add(new_priority)
    db.commit()
    db.refresh(new_priority)
    return new_priority

def update_priority(db: Session, priority_id: UUID, data: PriorityUpdate, user_id: UUID) -> Priority:
    priority = get_priority_by_id(db, priority_id)

    model_utils.update_model_fields(priority, data)
    priority.modified_by = user_id
    db.commit()
    db.refresh(priority)
    return priority

def delete_priority(db: Session, priority_id: UUID) -> None:
    priority = get_priority_by_id(db, priority_id)
    db.delete(priority)
    db.commit()

def get_priorities(db: Session):
    priorities = db.query(Priority).all()

    return priorities

def get_priority_by_id(db: Session, priority_id: UUID) -> Priority:
    priority = db.query(Priority).filter(Priority.id == priority_id).first()
    if not priority:
        raise HTTPException(status_code=404, detail="Priority not found")
    return priority
