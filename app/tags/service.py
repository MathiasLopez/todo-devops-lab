# tags/service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID

from ..utils import model_utils
from ..entities.tag import Tag
from ..entities.task_tag import task_tags
from .models import TagCreate, TagUpdate
from ..boards.access import check_user_permissions
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

def delete_tag(db: Session, tag_id: UUID, user_id: UUID, force: bool = False) -> None:
    tag = get_tag_by_id(db, tag_id, user_id)
    check_user_permissions(db, tag.board_id, user_id, required_permission=PERM_TAG_MANAGE)

    linked = (
        db.query(task_tags.c.task_id)
        .filter(task_tags.c.tag_id == tag_id)
        .count()
    )
    if linked and not force:
        raise HTTPException(
            status_code=409,
            detail="Tag is assigned to tasks; set force=true to delete it and remove the associations",
        )

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
