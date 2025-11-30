from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .mixins import AuditMixin
from .base import Base
from .task_tag import task_tags
import uuid

class Tag(Base, AuditMixin):
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(100), nullable=False)

    tasks = relationship("Task", secondary=task_tags, back_populates="tags")
