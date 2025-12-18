# entities/boardUserPermissions.py
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from .mixins import AuditMixin
from .base import Base

class BoardUserPermission(Base, AuditMixin):
    __tablename__ = "board_user_permissions"

    __table_args__ = (
        UniqueConstraint('board_id', 'user_id', name='unique_board_user'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    board_id = Column(UUID(as_uuid=True), ForeignKey("boards.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)