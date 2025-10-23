from fastapi import HTTPException
from sqlalchemy.orm import Session
from . import model
from ..entities.board import Board
from uuid import UUID

def create(db: Session, board_in: model.BoardCreate, user_id: UUID) -> Board:
    new_board = Board(**board_in.model_dump(), created_by=user_id, modified_by=user_id)
    db.add(new_board)
    db.commit()
    db.refresh(new_board)
    return new_board

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

def get_all(db: Session):
    return db.query(Board).all()

def get_by_id(db: Session, id:UUID) -> Board:
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