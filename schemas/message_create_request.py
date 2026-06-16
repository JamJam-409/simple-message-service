from pydantic import BaseModel


class MessageCreateRequest(BaseModel):
    """Request body for creating a message."""

    sender: str
    recipient: str
    content: str
