from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..entities.boardUserPermission import BoardUserPermission
from . import model
from ..entities.board import Board
from ..entities.boardColumn import BoardColumn
from ..entities.tag import Tag
from uuid import UUID
from ..utils import model_utils

def create(db: Session, board_in: model.BoardCreate, user_id: UUID) -> Board:
    try:
        with db.begin():
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
            db.flush()

            board_user_permission = BoardUserPermission(
                board_id=new_board.id,
                user_id=user_id,
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

            db.refresh(new_board)
            return new_board
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def update(db: Session, board_id: UUID, board_in: model.BoardUpdate, user_id: UUID) -> Board:
    board = get_by_id(db, board_id, user_id)
    model_utils.update_model_fields(board, board_in)
    board.modified_by = user_id
    db.commit()
    db.refresh(board)

    return board

def delete(db: Session, board_id:UUID, user_id:UUID) -> None:
    board = get_by_id(db, board_id, user_id)
    db.delete(board)
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
    return check_user_permissions(db, board_id, user_id)

def check_user_permissions(db: Session, board_id: UUID, user_id: UUID)  -> Board:
    """
    Checks whether a user has access to a board.
    Returns an HTTP 403 if the user not has permissions.
    """

    board = db.get(Board, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    # TODO: If the user is the owner, we could give them direct access. 
    #If we decided this, we would not have to add the record to the permissions table for the creator.
    # if board.created_by == user_id:
    #     return board

    has_permission = (
        db.query(BoardUserPermission)
        .filter_by(board_id=board_id, user_id=user_id)
        .first()
    )

    if not has_permission:
        raise HTTPException(status_code=403, detail="Board not shared with you")

    return board
