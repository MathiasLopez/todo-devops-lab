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
from ..entities.task_tag import task_tags
from uuid import UUID
from ..utils import model_utils
from ..entities.role import Role, RoleScope
from ..entities.permission import Permission
from ..entities.rolePermission import RolePermission
from ..auth.models import AuthContext
from app.auth.access import require_global_permission, find_global_role_with_permission
from app.auth.permissions import PERM_BOARD_CREATE
from .permissions import (
    PERM_BOARD_VIEW,
    PERM_BOARD_UPDATE,
    PERM_BOARD_DELETE,
    PERM_BOARD_MANAGE_MEMBERS,
)
from .access import check_user_permissions

def create(db: Session, board_in: model.BoardCreate, user_id: UUID) -> Board:
    require_global_permission(db, user_id, PERM_BOARD_CREATE)

    members = board_in.members or []
    board_roles_map = _get_board_roles_map(db)
    _validate_board_members(members, board_roles_map)

    try:
        if board_in.columns:
            _validate_columns(board_in.columns)

        if board_in.tags:
            _validate_tags(board_in.tags)

        board_data = board_in.model_dump(exclude={"columns", "tags", "members"})
        new_board = Board(**board_data, created_by=user_id, modified_by=user_id)
        db.add(new_board)
        db.flush()  # to get new_board.id

        _assign_board_members(db, new_board.id, members, user_id)

        if board_in.columns:
            _add_board_columns(db, new_board.id, board_in.columns, user_id)

        if board_in.tags:
            _add_board_tags(db, new_board.id, board_in.tags, user_id)

        db.commit()
        db.refresh(new_board)
        return new_board
    except SQLAlchemyError as e:
        db.rollback()
        raise e
    except Exception:
        db.rollback()
        raise

def update(db: Session, board_id: UUID, board_in: model.BoardUpdate, user_id: UUID, force: bool = False) -> Board:
    ctx = check_user_permissions(db, board_id, user_id, required_permission=PERM_BOARD_UPDATE)

    try:
        if board_in.columns is not None:
            _apply_column_patch(db, board_id, board_in.columns, user_id)

        if board_in.tags is not None:
            _replace_board_tags(db, board_id, board_in.tags, user_id, force=force)

        if board_in.members is not None:
            board_roles_map = _get_board_roles_map(db)
            _validate_board_members(board_in.members, board_roles_map)
            db.query(BoardUserPermission).filter_by(board_id=board_id).delete(synchronize_session=False)
            _assign_board_members(db, board_id, board_in.members, user_id)

        model_utils.update_model_fields(ctx.board, board_in, exclude={"columns", "tags", "members"})
        ctx.board.modified_by = user_id
        db.commit()
        db.refresh(ctx.board)

        return ctx.board
    except SQLAlchemyError as e:
        db.rollback()
        raise e
    except Exception:
        db.rollback()
        raise

def delete(db: Session, board_id:UUID, user_id:UUID) -> None:
    ctx = check_user_permissions(db, board_id, user_id, required_permission=PERM_BOARD_DELETE)
    # Remove board-member links first to satisfy FK constraint
    db.query(BoardUserPermission).filter_by(board_id=board_id).delete(synchronize_session=False)
    db.delete(ctx.board)
    db.commit()

def get_all(db: Session, user_id: UUID):
    # If the user holds a global role granting board.view, return every board; otherwise keep the member-based query.
    if find_global_role_with_permission(db, user_id, PERM_BOARD_VIEW):
        return db.query(Board).all()

    query = (
        select(Board)
        .join(BoardUserPermission, Board.id == BoardUserPermission.board_id)
        .join(Role, Role.id == BoardUserPermission.role_id)
        .join(RolePermission, RolePermission.role_id == Role.id)
        .join(Permission, Permission.id == RolePermission.permission_id)
        .where(
            BoardUserPermission.user_id == user_id,
            Permission.name == PERM_BOARD_VIEW,
        )
        .distinct()
    )
    result = db.execute(query).scalars().all()
    return result

def get_by_id(db: Session, board_id:UUID, user_id: UUID):
    ctx = check_user_permissions(db, board_id, user_id, required_permission=PERM_BOARD_VIEW)
    return ctx.board

def _get_board_roles_map(db: Session) -> dict[UUID, Role]:
    roles = (
        db.query(Role)
        .filter(Role.scope == RoleScope.BOARD.value)
        .all()
    )
    if not roles:
        raise HTTPException(status_code=500, detail="Board roles are not configured")
    return {role.id: role for role in roles}


def _validate_board_members(members: list[model.BoardMemberCreate], board_roles_map: dict[UUID, Role]) -> None:
    if not members:
        raise HTTPException(status_code=400, detail="Board must have at least one member")

    highest_level = max(role.level for role in board_roles_map.values())
    highest_role_ids = {role_id for role_id, role in board_roles_map.items() if role.level == highest_level}

    seen_user_ids: set[UUID] = set()
    has_highest_role = False

    for member in members:
        if member.user_id in seen_user_ids:
            raise HTTPException(status_code=400, detail=f"Duplicate member user_id: {member.user_id}")
        seen_user_ids.add(member.user_id)

        if member.role_id not in board_roles_map:
            raise HTTPException(status_code=400, detail="Role not configured for board scope")

        if member.role_id in highest_role_ids:
            has_highest_role = True

    if not has_highest_role:
        raise HTTPException(
            status_code=400,
            detail="At least one member must have the highest-level board role",
        )


def _assign_board_members(
    db: Session,
    board_id: UUID,
    members: list[model.BoardMemberCreate],
    actor_id: UUID,
) -> None:
    for member in members:
        db.add(
            BoardUserPermission(
                board_id=board_id,
                user_id=member.user_id,
                role_id=member.role_id,
                created_by=actor_id,
                modified_by=actor_id,
            )
        )


def _validate_columns(columns: list[model.ColumnCreate]) -> None:
    seen_titles: set[str] = set()
    for column in columns:
        title = (column.title or "").strip()
        if not title:
            raise HTTPException(status_code=400, detail="Column title cannot be empty")
        normalized = title.lower()
        if normalized in seen_titles:
            raise HTTPException(status_code=400, detail=f"Duplicate column title: {title}")
        seen_titles.add(normalized)


def _add_board_columns(db: Session, board_id: UUID, columns: list[model.ColumnCreate], user_id: UUID) -> None:
    for column in columns:
        column_description = (column.description or "").strip()
        if not column_description:
            column_description = ""
        new_column = BoardColumn(
            board_id=board_id,
            title=column.title,
            description=column_description,
            created_by=user_id,
            modified_by=user_id
        )
        db.add(new_column)


def _apply_column_patch(
    db: Session,
    board_id: UUID,
    columns: list[model.ColumnCreate],
    user_id: UUID,
) -> None:
    _validate_columns(columns)

    existing_columns = (
        db.query(BoardColumn)
        .filter(BoardColumn.board_id == board_id)
        .all()
    )
    existing_by_id = {column.id: column for column in existing_columns}
    processed_ids: set[UUID] = set()

    for column in columns:
        if column.id:
            existing = existing_by_id.get(column.id)
            if not existing:
                raise HTTPException(status_code=404, detail=f"Column {column.id} not found")
            model_utils.update_model_fields(existing, column, exclude={"id"})
            existing.modified_by = user_id
            processed_ids.add(column.id)
        else:
            _add_board_columns(db, board_id, [column], user_id)

    for column_id, column in existing_by_id.items():
        if column_id in processed_ids:
            continue
        _ensure_column_has_no_tasks(db, column_id)
        db.delete(column)


def _ensure_column_has_no_tasks(db: Session, column_id: UUID) -> None:
    task_exists = (
        db.query(Task.id)
        .filter(Task.column_id == column_id)
        .first()
    )
    if task_exists:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete column while tasks exist; move or delete tasks first",
        )


def _validate_tags(tags: list[model.TagCreate]) -> None:
    seen: set[str] = set()
    for tag in tags:
        title = (tag.title or "").strip()
        if not title:
            raise HTTPException(status_code=400, detail="Tag title cannot be empty")
        normalized = title.lower()
        if normalized in seen:
            raise HTTPException(status_code=400, detail=f"Duplicate tag title: {title}")
        seen.add(normalized)


def _add_board_tags(db: Session, board_id: UUID, tags: list[model.TagCreate], user_id: UUID) -> None:
    for tag in tags:
        new_tag = Tag(
            board_id=board_id,
            title=tag.title,
            created_by=user_id,
            modified_by=user_id
        )
        db.add(new_tag)


def _replace_board_tags(db: Session, board_id: UUID, tags: list[model.TagCreate], user_id: UUID, force: bool = False) -> None:
    _validate_tags(tags)

    def _normalize(title: str | None) -> str:
        return (title or "").strip().lower()

    incoming_by_title = {
        _normalize(tag.title): tag
        for tag in tags
    }

    existing_tags = db.query(Tag).filter_by(board_id=board_id).all()
    existing_by_title = {
        _normalize(tag.title): tag
        for tag in existing_tags
    }

    for normalized_title, tag in existing_by_title.items():
        if normalized_title not in incoming_by_title:
            _ensure_tag_not_in_use(db, tag.id, tag.title, force=force)
            db.delete(tag)

    for normalized_title, incoming_tag in incoming_by_title.items():
        existing = existing_by_title.get(normalized_title)
        if existing:
            if existing.title != incoming_tag.title:
                existing.title = incoming_tag.title
                existing.modified_by = user_id
            continue

        _add_board_tags(db, board_id, [incoming_tag], user_id)


def _ensure_tag_not_in_use(db: Session, tag_id: UUID, title: str, force: bool = False) -> None:
    if force:
        return
    task_exists = (
        db.query(task_tags.c.task_id)
        .filter(task_tags.c.tag_id == tag_id)
        .first()
    )
    if task_exists:
        raise HTTPException(
            status_code=409,
            detail=f"Tag '{title}' is assigned to tasks; remove those associations before deleting it",
        )


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
