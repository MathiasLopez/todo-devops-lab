from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class TaskBase(BaseModel):
    title: str
    description: str
    assigned: Optional[UUID] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    assigned: Optional[UUID] = None

class TaskResponse(TaskBase):
    id: UUID
    created_by: UUID
    created_at: datetime
    modified_by: UUID
    modified_at: datetime
    is_completed: bool