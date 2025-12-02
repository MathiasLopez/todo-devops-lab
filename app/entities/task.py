# models/task.py
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .mixins import AuditMixin
import uuid
from .base import Base

# Needed for SQLAlchemy to establish the relationship
from .boardColumn import BoardColumn
from .taskPriority import TaskPriority
from .tag import Tag
from .task_tag import task_tags

class Task(Base, AuditMixin):
    __tablename__ = 'tasks'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    start_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    assigned = Column(UUID(as_uuid=True), nullable=True)

    column_id = Column(UUID(as_uuid=True), ForeignKey("board_columns.id"), nullable=False)
    priority_id = Column(UUID(as_uuid=True), ForeignKey("task_priorities.id"), nullable=False)

    column = relationship("BoardColumn", back_populates="tasks")
    priority = relationship("TaskPriority")
    tags = relationship("Tag", secondary=task_tags, back_populates="tasks")
