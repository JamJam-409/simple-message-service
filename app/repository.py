from uuid import UUID

from sqlalchemy import select, true
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Message
from app.schemas import MessageActionResponse, MessageCreateRequest


class MessageRepository:
    """Database access layer for messages."""

    def __init__(self, db: Session):
        """Initialize the repository with a database session."""
        self.db = db

    def create(self, request: MessageCreateRequest):
        """Create and persist a message."""
        message = Message(
            recipient=request.recipient.lower(),
            sender=request.sender.lower(),
            content=request.content,
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        return message

    def get_unread_messages(self, recipient: str) -> list[Message]:
        """Return unread messages for a recipient."""
        messages = list(
            self.db.scalars(
                select(Message).where(
                    Message.recipient == recipient,
                    Message.is_read.is_(False)
                )
            ).all()
        )
        for message in messages:
            message.is_read = True


        return messages


    def delete(self, message_id: UUID) -> int:
        """Delete one message by id and return the deleted row count."""
        deleted_count = self.db.query(Message).filter(
            Message.id == message_id
        ).delete(synchronize_session=False)

        self.db.commit()
        return deleted_count



    def bulk_delete(self, message_ids: list[UUID]) -> int:
        """Delete multiple messages and return the deleted row count."""
        deleted_count = self.db.query(Message).filter(
            Message.id.in_(message_ids)
        ).delete(synchronize_session=False)

        self.db.commit()
        return deleted_count


    def get_messages_by_index(
        self,
        recipient: str,
        start_index: int,
        stop_index: int | None,
    ) -> list[Message]:
        """Return recipient messages between optional start and stop indexes."""
        query = select(Message).where(
            Message.recipient == recipient
        ).order_by(Message.created_at).offset(start_index)

        # Set limit when stop index exists
        if stop_index is not None:
            query = query.limit(stop_index - start_index)

        return list(self.db.scalars(query).all())
