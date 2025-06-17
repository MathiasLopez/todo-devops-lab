from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.entities.task import Priority

class TaskBase(BaseModel):
    title: str
    description: str
    priority: Priority = Priority.Medium

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: UUID
    is_completed: bool
    
    model_config = ConfigDict(from_attributes=True)