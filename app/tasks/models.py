# tasks/models.py
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from ..priorities.models import PriorityResponse
from ..tags.models import TagResponse
from ..attachments.models import AttachmentResponse

class SubtaskResponse(BaseModel):
    id: UUID
    title: str

    model_config = ConfigDict(from_attributes=True)

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority_id: UUID
    assigned: Optional[UUID] = None
    tags: Optional[List[UUID]] = None
    parent_id: Optional[UUID] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    title: Optional[str] = None
    priority_id: Optional[UUID] = None
    column_id: Optional[UUID] = None

class TaskResponse(TaskBase):
    id: UUID
    created_by: UUID
    created_at: datetime
    modified_by: UUID
    modified_at: datetime

    column_id: UUID
    priority: PriorityResponse
    tags: List[TagResponse]
    parent: Optional[SubtaskResponse] = None
    subtasks: List[SubtaskResponse] = []
    attachments: List[AttachmentResponse] = []

    model_config = ConfigDict(from_attributes=True)


class TaskSearchItem(BaseModel):
    id: UUID
    title: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
