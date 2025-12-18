# tags/models.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class TagBase(BaseModel):
    title: str

class TagCreate(TagBase):
    pass

class TagUpdate(TagBase):
    pass

class TagResponse(TagBase):
    id: UUID
    title: str

    created_by: UUID
    created_at: datetime
    modified_by: UUID
    modified_at: datetime

