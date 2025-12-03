# schemas/column.py
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class ColumnCreate(BaseModel):
    title: str
    description: Optional[str] = None

class ColumnUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class ColumnResponse(BaseModel):
    id: UUID
    board_id: UUID
    title: str
    description: Optional[str]
