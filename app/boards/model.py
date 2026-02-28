from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

from ..columns.models import ColumnCreate
from ..tags.models import TagCreate

class BoardBase(BaseModel):
    title: str
    description: Optional[str] = None

class BoardCreate(BoardBase):
    columns: Optional[List[ColumnCreate]] = None
    tags: Optional[List[TagCreate]] = None

class BoardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class BoardResponse(BoardBase):
    id: UUID
    created_by: UUID
    created_at: datetime
    modified_by: UUID
    modified_at: datetime
