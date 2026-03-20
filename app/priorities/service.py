# priorities/service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID

from ..utils import model_utils
from ..entities.priority import Priority
from .constants import SYSTEM_PRIORITY_IDS
from .models import PriorityCreate, PriorityUpdate


def _normalize_color_or_raise(color: str, *, required: bool = True) -> str:
    if color is None:
        if required:
            raise HTTPException(status_code=422, detail="Color cannot be null")
        return None
    return color.upper()

def create_priority(db: Session, data: PriorityCreate, user_id: UUID) -> Priority:
    payload = data.model_dump(exclude_unset=True)
    payload["color"] = _normalize_color_or_raise(payload.get("color"), required=True)
    new_priority = Priority(**payload, created_by=user_id, modified_by=user_id)
    db.add(new_priority)
    db.commit()
    db.refresh(new_priority)
    return new_priority

def update_priority(db: Session, priority_id: UUID, data: PriorityUpdate, user_id: UUID) -> Priority:
    priority = get_priority_by_id(db, priority_id)
    if priority.id in SYSTEM_PRIORITY_IDS:
        raise HTTPException(status_code=400, detail="System priorities cannot be modified")

    update_payload = data.model_dump(exclude_unset=True)
    if "color" in update_payload:
        update_payload["color"] = _normalize_color_or_raise(update_payload["color"], required=True)

    model_utils.update_model_fields(priority, PriorityUpdate(**update_payload))
    priority.modified_by = user_id
    db.commit()
    db.refresh(priority)
    return priority

def delete_priority(db: Session, priority_id: UUID) -> None:
    priority = get_priority_by_id(db, priority_id)
    if priority.id in SYSTEM_PRIORITY_IDS:
        raise HTTPException(status_code=400, detail="System priorities cannot be deleted")
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
