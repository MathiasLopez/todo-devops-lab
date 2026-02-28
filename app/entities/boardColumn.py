# entities/boardColumn.py
from sqlalchemy import Column as SAColumn, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .mixins import AuditMixin
import uuid

from .base import Base

class BoardColumn(Base, AuditMixin):
    __tablename__ = "board_columns"

    id = SAColumn(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    board_id = SAColumn(UUID(as_uuid=True), ForeignKey("boards.id"), nullable=False)
    title = SAColumn(String(100), nullable=False)
    description = SAColumn(String, nullable=True)

    # Relationships
    board = relationship("Board", back_populates="columns")
    tasks = relationship("Task", back_populates="column", cascade="all, delete-orphan")
