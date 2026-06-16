from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, String, Text, UUID, func, Index

from app.database import Base


class Message(Base):
    """Database model for a message."""

    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    sender = Column(String(255), nullable=False)
    recipient = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)

    # Create composite index for recipient and is_read
    __table_args__ = (
        Index("idx_recipient_is_read", "recipient", "is_read"),
    )