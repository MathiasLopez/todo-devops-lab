# entities/tag.py
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .mixins import AuditMixin
from .base import Base
from .task_tag import task_tags
import uuid

class Tag(Base, AuditMixin):
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    board_id = Column(UUID(as_uuid=True), ForeignKey("boards.id"), nullable=False)
    title = Column(String(100), nullable=False)

    board = relationship("Board", back_populates="tags")
    tasks = relationship("Task", secondary=task_tags, back_populates="tags")
