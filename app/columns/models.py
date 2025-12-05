# schemas/column.py
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

from ..tasks.models import TaskResponse

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

    created_by: UUID
    created_at: datetime
    modified_by: UUID
    modified_at: datetime

class ColumnWithTaskResponse(ColumnResponse):
    #tasks: list[FullTaskResponse]
    tasks: list[TaskResponse]
