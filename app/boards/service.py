from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..entities.boardUserPermission import BoardUserPermission
from . import model
from ..entities.board import Board
from uuid import UUID

def create(db: Session, board_in: model.BoardCreate, user_id: UUID) -> Board:
    try:
        with db.begin():
            new_board = Board(**board_in.model_dump(), created_by=user_id, modified_by=user_id)
            db.add(new_board)
            db.flush()

            board_user_permission = BoardUserPermission(
                board_id=new_board.id,
                user_id=user_id,
                created_by=user_id,
                modified_by=user_id
            )
            db.add(board_user_permission)

            db.refresh(new_board)
            return new_board
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def update(db: Session, id: UUID, board_in: model.BoardUpdate, user_id: UUID) -> Board:
    board = get_by_id(db, id)
    update_model_fields(board, board_in)
    board.modified_by = user_id
    db.commit()
    db.refresh(board)

    return board

def delete(db: Session, id:UUID) -> None:
    board = get_by_id(db, id)
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

def _get_by_id(db: Session, id:UUID) -> Board:
    board = db.get(Board, id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    return board

def update_model_fields(model, update_obj) -> None:
    """
    Update the model attributes according to the non None values of the Pydantic object.
    """
    for field, value in update_obj.model_dump(exclude_unset=True).items():
        setattr(model, field, value)

def get_by_id(db: Session, id:UUID, user_id: UUID):
    board = _get_by_id(db, id)
    has_permission = db.query(BoardUserPermission).filter_by(
        board_id=board.id,
        user_id=user_id
    ).first()

    if not has_permission:
        raise HTTPException(status_code=403, detail="Board not shared with you")
    
    return board