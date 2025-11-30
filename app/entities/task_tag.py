# entities/task_tag.py
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from .base import Base

task_tags = Table(
    "task_tags",
    Base.metadata,
    Column("task_id", UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)
