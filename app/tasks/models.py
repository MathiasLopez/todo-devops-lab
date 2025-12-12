from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from ..priorities.models import PriorityResponse
from ..tags.models import TagResponse

class TaskBase(BaseModel):
    title: str
    description: str
    priority_id: UUID
    assigned: Optional[UUID] = None
    tags: Optional[List[UUID]] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority_id: Optional[UUID] = None
    tags: Optional[List[UUID]] = None

class TaskResponse(TaskBase):
    id: UUID
    created_by: UUID
    created_at: datetime
    modified_by: UUID
    modified_at: datetime

    priority: PriorityResponse
    tags: List[TagResponse]