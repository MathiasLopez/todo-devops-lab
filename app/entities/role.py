# entities/role.py
import enum
import uuid

from sqlalchemy import Column, String, Integer, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .mixins import AuditMixin
from .base import Base


class RoleScope(str, enum.Enum):
    GLOBAL = "global"
    BOARD = "board"


class Role(Base, AuditMixin):
    __tablename__ = "roles"
    __table_args__ = (
        UniqueConstraint("name", "scope", name="uq_role_name_scope"),
        CheckConstraint("scope in ('global', 'board')", name="ck_role_scope_allowed"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)
    description = Column(String, nullable=True)
    level = Column(Integer, nullable=False)
    scope = Column(String(16), nullable=False, default=RoleScope.BOARD.value)

    board_users = relationship("BoardUserPermission", back_populates="role", cascade="all, delete-orphan")
    permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")
