from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
from ..database.core import Base

class BoardUserPermission(Base):
    __tablename__ = "board_user_permissions"

    __table_args__ = (
        UniqueConstraint('board_id', 'user_id', name='unique_board_user'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    board_id = Column(UUID(as_uuid=True), ForeignKey("boards.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    created_by = Column(UUID(as_uuid=True), nullable=False)
    modified_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    modified_by = Column(UUID(as_uuid=True), nullable=False)