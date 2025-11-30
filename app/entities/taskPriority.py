# models/task_priority.py
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from .mixins import AuditMixin
import uuid

from .base import Base

class TaskPriority(Base, AuditMixin):
    __tablename__ = "task_priorities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(50), nullable=False)
