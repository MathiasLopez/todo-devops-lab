# entities/permission.py
import uuid

from sqlalchemy import Column, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .mixins import AuditMixin
from .base import Base


class Permission(Base, AuditMixin):
    __tablename__ = "permissions"
    __table_args__ = (
        UniqueConstraint("name", name="permissions_name_key"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(80), nullable=False)
    description = Column(String, nullable=True)

    roles = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")
