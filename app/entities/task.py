from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid
from datetime import datetime, timezone
import enum
from ..database.core import Base
from sqlalchemy.orm import relationship
from ..entities.board import Board # Required for relation with board

class Priority(enum.Enum):
    Normal = 0
    Low = 1
    Medium = 2
    High = 3
    Top = 4

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    is_completed = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    priority = Column(Enum(Priority), nullable=False, default=Priority.Medium)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    assigned = Column(UUID(as_uuid=True), nullable=True)
    modified_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    modified_by = Column(UUID(as_uuid=True), nullable=False)

    # Mandatory relationship with Board
    board_id = Column(UUID(as_uuid=True), ForeignKey("boards.id"), nullable=False)
    board = relationship("Board", back_populates="tasks")
