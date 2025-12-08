# services/tag_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID

from ..entities.boardUserPermission import BoardUserPermission

from ..utils import model_utils
from ..entities.tag import Tag
from .models import TagCreate, TagUpdate

def create_tag(db: Session, data: TagCreate, user_id: UUID) -> Tag:
    new_tag = Tag(**data.model_dump(), created_by = user_id, modified_by=user_id)
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return new_tag

def update_tag(db: Session, tag_id: UUID, data: TagUpdate, user_id: UUID) -> Tag:
    tag = get_tag_by_id(db, tag_id)

    model_utils.update_model_fields(tag, data)
    tag.modified_by = user_id
    db.commit()
    db.refresh(tag)
    return tag

def delete_tag(db: Session, tag_id: UUID, user_id:UUID) -> None:
    tag = get_tag_by_id(db, tag_id)
    db.delete(tag)
    db.commit()


def get_tags(db: Session, board_id: UUID, user_id: UUID):
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
    
    query = db.query(Tag).filter(Tag.board_id == board_id)
    tags = query.all()

    return tags


def get_tag_by_id(db: Session, tag_id: UUID) -> Tag:
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag
