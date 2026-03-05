# users/models.py
from pydantic import BaseModel
from uuid import UUID

class UserResponse(BaseModel):
    id: UUID
    username: str
