from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.entities.task import Priority

class TaskBase(BaseModel):
    title: str
    description: str
    assigned: Optional[UUID] = None
    priority: Priority = Priority.Medium

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Priority] = None
    is_completed: Optional[bool] = None
    assigned: Optional[UUID] = None

class TaskResponse(TaskBase):
    id: UUID
    is_completed: bool
    
    model_config = ConfigDict(from_attributes=True)