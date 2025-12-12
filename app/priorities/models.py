# priorities/models.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class PriorityBase(BaseModel):
    title: str

class PriorityCreate(PriorityBase):
    pass

class PriorityUpdate(PriorityBase):
    pass

class PriorityResponse(PriorityBase):
    id: UUID

    created_by: UUID
    created_at: datetime
    modified_by: UUID
    modified_at: datetime