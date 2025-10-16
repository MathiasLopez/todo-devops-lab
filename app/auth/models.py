from uuid import UUID
from pydantic import BaseModel

class AuthContext(BaseModel):
    user_id: UUID
    token: str