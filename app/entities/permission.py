# entities/permission.py
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from .mixins import AuditMixin
from .base import Base

class Permission(Base, AuditMixin):
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(80), nullable=False, unique=True)
    description = Column(String, nullable=True)

    roles = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")
