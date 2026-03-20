# priorities/models.py
from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator

HEX_COLOR_PATTERN = r"^#(?:[0-9a-fA-F]{6})$"


class PriorityBase(BaseModel):
    title: str
    color: str = Field(
        ...,
        pattern=HEX_COLOR_PATTERN,
        description="Hex color in #RRGGBB format",
    )

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("title cannot be blank")
        return v.strip()


class PriorityCreate(PriorityBase):
    pass


class PriorityUpdate(BaseModel):
    title: Optional[str] = None
    color: Optional[str] = Field(
        default=None,
        pattern=HEX_COLOR_PATTERN,
        description="Hex color in #RRGGBB format",
    )

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v.strip():
            raise ValueError("title cannot be blank")
        return v.strip()


class PriorityResponse(PriorityBase):
    id: UUID

    created_by: UUID
    created_at: datetime
    modified_by: UUID
    modified_at: datetime

    model_config = ConfigDict(from_attributes=True)
