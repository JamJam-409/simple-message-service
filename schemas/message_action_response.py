from pydantic import BaseModel


class MessageActionResponse(BaseModel):
    """Response returned after a message action completes."""

    message: str
