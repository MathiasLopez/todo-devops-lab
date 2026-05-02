# entities/attachment.py
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from .base import Base


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String, nullable=False)
    minio_key = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    task = relationship("Task", back_populates="attachments")
