from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MessageActionResponse(BaseModel):
    """Response returned after a message action completes."""

    message: str

class MessageBulkDeleteRequest(BaseModel):
    """Request body for deleting multiple messages."""

    message_ids: list[UUID]

class MessageCreateRequest(BaseModel):
    """Request body for creating a message."""

    sender: str
    recipient: str
    content: str

class MessageGetResponse(BaseModel):
    """Response schemas for returning message details."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sender: str
    time: datetime = Field(validation_alias="created_at")
    is_read: bool
    content: str
