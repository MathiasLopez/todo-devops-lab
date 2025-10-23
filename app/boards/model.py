from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

class BoardBase(BaseModel):
    title: str
    description: str

class BoardCreate(BoardBase):
    pass

class BoardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class BoardResponse(BoardBase):
    id: UUID
    created_by: UUID
    created_at: datetime
    modified_by: UUID
    modified_at: datetime