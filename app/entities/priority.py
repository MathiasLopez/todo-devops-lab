# entities/priority.py
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from .mixins import AuditMixin
import uuid

from .base import Base

class Priority(Base, AuditMixin):
    __tablename__ = "priorities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(50), nullable=False)
