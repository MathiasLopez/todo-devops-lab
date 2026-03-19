from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..entities.boardUserPermission import BoardUserPermission
from . import model
from ..entities.board import Board
from ..entities.boardColumn import BoardColumn
from ..entities.tag import Tag
from ..entities.task import Task
from uuid import UUID
from ..utils import model_utils
from ..entities.role import Role
from ..auth.models import AuthContext
from ..users import service as user_service
from ..users.models import UserResponse
from .permissions import (
    PERM_BOARD_VIEW,
    PERM_BOARD_UPDATE,
    PERM_BOARD_DELETE,
    PERM_BOARD_MANAGE_MEMBERS
)
from .access import check_user_permissions

def create(db: Session, board_in: model.BoardCreate, user_id: UUID) -> Board:
    try:
        owner_role = _get_role_by_name(db, "owner")

        # Validations happen before mutating the session to avoid partial writes
        if board_in.columns:
            seen_columns = set()
            for column in board_in.columns:
                title = (column.title or "").strip()
                if not title:
                    raise HTTPException(status_code=400, detail="Column title cannot be empty")
                normalized = title.lower()
                if normalized in seen_columns:
                    raise HTTPException(status_code=400, detail=f"Duplicate column title: {title}")
                seen_columns.add(normalized)

        if board_in.tags:
            seen_tags = set()
            for tag in board_in.tags:
                title = (tag.title or "").strip()
                if not title:
                    raise HTTPException(status_code=400, detail="Tag title cannot be empty")
                normalized = title.lower()
                if normalized in seen_tags:
                    raise HTTPException(status_code=400, detail=f"Duplicate tag title: {title}")
                seen_tags.add(normalized)

        board_data = board_in.model_dump(exclude={"columns", "tags"})
        new_board = Board(**board_data, created_by=user_id, modified_by=user_id)
        db.add(new_board)
        db.flush()  # to get new_board.id

        board_user_permission = BoardUserPermission(
            board_id=new_board.id,
            user_id=user_id,
            role_id=owner_role.id,
            created_by=user_id,
            modified_by=user_id
        )
        db.add(board_user_permission)

        if board_in.columns:
            for column in board_in.columns:
                column_description = (column.description or "").strip()
                if not column_description:
                    column_description = ""
                new_column = BoardColumn(
                    board_id=new_board.id,
                    title=column.title,
                    description=column_description,
                    created_by=user_id,
                    modified_by=user_id
                )
                db.add(new_column)

        if board_in.tags:
            for tag in board_in.tags:
                new_tag = Tag(
                    board_id=new_board.id,
                    title=tag.title,
                    created_by=user_id,
                    modified_by=user_id
                )
                db.add(new_tag)

        db.commit()
        db.refresh(new_board)
        return new_board
    except SQLAlchemyError as e:
        db.rollback()
        raise e
    except Exception:
        db.rollback()
        raise

def update(db: Session, board_id: UUID, board_in: model.BoardUpdate, user_id: UUID) -> Board:
    ctx = check_user_permissions(db, board_id, user_id, required_permission=PERM_BOARD_UPDATE)
    model_utils.update_model_fields(ctx.board, board_in)
    ctx.board.modified_by = user_id
    db.commit()
    db.refresh(ctx.board)

    return ctx.board

def delete(db: Session, board_id:UUID, user_id:UUID) -> None:
    ctx = check_user_permissions(db, board_id, user_id, required_permission=PERM_BOARD_DELETE)
    # Remove board-member links first to satisfy FK constraint
    db.query(BoardUserPermission).filter_by(board_id=board_id).delete(synchronize_session=False)
    db.delete(ctx.board)
    db.commit()

def get_all(db: Session, user_id: UUID):
    query = (
        select(Board)
        .join(BoardUserPermission, Board.id == BoardUserPermission.board_id)
        .where(BoardUserPermission.user_id == user_id)
    )
    result = db.execute(query).scalars().all()
    return result

def get_by_id(db: Session, board_id:UUID, user_id: UUID):
    ctx = check_user_permissions(db, board_id, user_id, required_permission=PERM_BOARD_VIEW)
    return ctx.board

def _get_role_by_name(db: Session, name: str) -> Role:
    role = db.query(Role).filter_by(name=name).one_or_none()
    if not role:
        raise HTTPException(status_code=500, detail=f"Role '{name}' is not configured")
    return role

def _get_role_by_id(db: Session, role_id: UUID) -> Role:
    role = db.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

def _ensure_role_not_higher(target_role: Role, actor_role: Role, message: str = "Operation not allowed"):
    if target_role.level > actor_role.level:
        raise HTTPException(status_code=403, detail=message)

def _ensure_not_last_owner(db: Session, board_id: UUID, exclude_user_id: UUID | None = None):
    query = (
        db.query(func.count(BoardUserPermission.id))
        .join(Role, Role.id == BoardUserPermission.role_id)
        .filter(BoardUserPermission.board_id == board_id, Role.name == "owner")
    )
    if exclude_user_id:
        query = query.filter(BoardUserPermission.user_id != exclude_user_id)
    owners = query.scalar()
    if owners == 0:
        raise HTTPException(status_code=409, detail="Board must have at least one owner")

def add_board_member(db: Session, board_id: UUID, payload: model.BoardMemberCreate, actor_id: UUID) -> model.BoardMemberResponse:
    ctx = check_user_permissions(
        db,
        board_id,
        actor_id,
        required_permission=PERM_BOARD_MANAGE_MEMBERS,
    )
    actor_role = ctx.role

    existing = (
        db.query(BoardUserPermission)
        .filter_by(board_id=board_id, user_id=payload.user_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="User is already a member of this board")

    role = _get_role_by_id(db, payload.role_id)
    _ensure_role_not_higher(role, actor_role, "Cannot assign a role higher than yours")

    new_member = BoardUserPermission(
        board_id=board_id,
        user_id=payload.user_id,
        role_id=payload.role_id,
        created_by=actor_id,
        modified_by=actor_id,
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    # TODO: send email notification to the added user

    return model.BoardMemberResponse(
        user_id=new_member.user_id,
        role_id=new_member.role_id
    )

def update_board_member(db: Session, board_id: UUID, user_id: UUID, payload: model.BoardMemberUpdate, actor_id: UUID) -> model.BoardMemberResponse:
    ctx = check_user_permissions(
        db,
        board_id,
        actor_id,
        required_permission=PERM_BOARD_MANAGE_MEMBERS,
    )
    actor_role = ctx.role

    member = (
        db.query(BoardUserPermission)
        .filter_by(board_id=board_id, user_id=user_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="User is not a member of this board")

    current_role = db.get(Role, member.role_id)
    _ensure_role_not_higher(current_role, actor_role, "You cannot modify a member with higher role")

    new_role = _get_role_by_id(db, payload.role_id)
    _ensure_role_not_higher(new_role, actor_role, "Cannot assign a role higher than yours")

    if user_id == actor_id and new_role.level > actor_role.level:
        raise HTTPException(status_code=403, detail="You cannot escalate your own privileges")

    if current_role.name == "owner" and new_role.name != "owner":
        _ensure_not_last_owner(db, board_id, exclude_user_id=user_id)

    member.role_id = payload.role_id
    member.modified_by = actor_id
    db.commit()
    db.refresh(member)

    return model.BoardMemberResponse(
        user_id=member.user_id,
        role_id=member.role_id
    )

def delete_board_member(db: Session, board_id: UUID, user_id: UUID, actor_id: UUID) -> None:
    ctx = check_user_permissions(
        db,
        board_id,
        actor_id,
        required_permission=PERM_BOARD_MANAGE_MEMBERS,
    )
    actor_role = ctx.role

    member = (
        db.query(BoardUserPermission)
        .filter_by(board_id=board_id, user_id=user_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="User is not a member of this board")

    member_role = db.get(Role, member.role_id)
    _ensure_role_not_higher(member_role, actor_role, "You cannot remove a member with higher role")

    if member_role.name == "owner":
        _ensure_not_last_owner(db, board_id, exclude_user_id=user_id)
        
    task_exists = (
        db.query(Task.id)
        .join(BoardColumn)
        .filter(
            BoardColumn.board_id == board_id,
            Task.assigned == user_id
        )
        .first()
    )

    if task_exists:
        raise HTTPException(status_code=409, detail="User has tasks assigned in this board; unassign them first")

    db.delete(member)
    db.commit()

def get_board_members(db: Session, board_id: UUID, auth_context: AuthContext) -> list[model.BoardMemberResponse]:
    check_user_permissions(db, board_id, auth_context.user_id, required_permission=PERM_BOARD_VIEW)

    rows = (
        db.query(BoardUserPermission.user_id, Role.id.label("role_id"))
        .join(Role, Role.id == BoardUserPermission.role_id)
        .filter(BoardUserPermission.board_id == board_id)
        .all()
    )
    if not rows:
        return []

    result = []
    for user_id, role_id in rows:
        result.append(model.BoardMemberResponse(user_id=user_id, role_id=role_id))
    return result
