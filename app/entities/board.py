# entities/board.py
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .mixins import AuditMixin
import uuid

# Needed for SQLAlchemy to establish the relationship
from .boardColumn import BoardColumn
from .tag import Tag

from .base import Base

class Board(Base, AuditMixin):
    __tablename__ = "boards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(100), nullable=False)
    description = Column(String, nullable=True)

    # Relation 1 -> N
    columns = relationship("BoardColumn", back_populates="board", cascade="all, delete-orphan")
    tags = relationship("Tag", back_populates="board", cascade="all, delete-orphan")

