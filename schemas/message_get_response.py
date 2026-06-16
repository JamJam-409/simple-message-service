from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MessageGetResponse(BaseModel):
    """Response schemas for returning message details."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sender: str
    time: datetime = Field(validation_alias="created_at")
    is_read: bool
    content: str
