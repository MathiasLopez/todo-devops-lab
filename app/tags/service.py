# tags/service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID

from ..utils import model_utils
from ..entities.tag import Tag
from .models import TagCreate, TagUpdate
from ..boards.service import check_user_permissions
from ..boards.permissions import PERM_BOARD_VIEW, PERM_TAG_MANAGE

def create_tag(db: Session, data: TagCreate, user_id: UUID, board_id: UUID) -> Tag:
    ctx = check_user_permissions(db, board_id, user_id, required_permission=PERM_TAG_MANAGE)
    new_tag = Tag(**data.model_dump(), board=ctx.board, created_by=user_id, modified_by=user_id)
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return new_tag

def update_tag(db: Session, tag_id: UUID, data: TagUpdate, user_id: UUID) -> Tag:
    tag = get_tag_by_id(db, tag_id, user_id)
    check_user_permissions(db, tag.board_id, user_id, required_permission=PERM_TAG_MANAGE)

    model_utils.update_model_fields(tag, data)
    tag.modified_by = user_id
    db.commit()
    db.refresh(tag)
    return tag

def delete_tag(db: Session, tag_id: UUID, user_id:UUID) -> None:
    tag = get_tag_by_id(db, tag_id, user_id)
    check_user_permissions(db, tag.board_id, user_id, required_permission=PERM_TAG_MANAGE)
    db.delete(tag)
    db.commit()

def get_tags(db: Session, board_id: UUID, user_id: UUID):
    ctx = check_user_permissions(db, board_id, user_id, required_permission=PERM_BOARD_VIEW)
    
    query = db.query(Tag).filter(Tag.board == ctx.board)
    tags = query.all()

    return tags

def get_tag_by_id(db: Session, tag_id: UUID, user_id: UUID) -> Tag:
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    check_user_permissions(db, tag.board_id, user_id, required_permission=PERM_BOARD_VIEW)
    return tag
