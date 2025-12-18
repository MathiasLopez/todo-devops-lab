# entities/mixins.py
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class UUIDMixin:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

class AuditMixin:
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    created_by = Column(UUID(as_uuid=True), nullable=False)
    modified_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    modified_by = Column(UUID(as_uuid=True), nullable=False)
