# attachments/models.py
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class AttachmentResponse(BaseModel):
    id: UUID
    task_id: UUID
    filename: str
    content_type: str
    file_size: int
    created_by: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DownloadResponse(BaseModel):
    url: str
    expires_in: int  # seconds
