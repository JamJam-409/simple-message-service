from uuid import UUID

from pydantic import BaseModel


class MessageBulkDeleteRequest(BaseModel):
    """Request body for deleting multiple messages."""

    message_ids: list[UUID]
