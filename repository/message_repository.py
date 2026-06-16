from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models.message import Message
from schemas.message_bulk_delete_request import MessageBulkDeleteRequest


class MessageRepository:
    """Database access layer for messages."""

    def __init__(self, db: Session):
        """Initialize the repository with a database session."""
        self.db = db

    def create(self, request):
        """Create and persist a message."""
        try:
            message = Message(
                recipient=request.recipient,
                sender=request.sender,
                content=request.content,
            )

            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)

            return message

        except SQLAlchemyError:
            self.db.rollback()
            raise

    def get_all(self) -> list[Message]:
        """Return all messages."""
        return self.db.scalars(select(Message)).all()

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
        # should not change db status in a get method
        return messages

    def mark_as_read(self, message_id: UUID) -> Message | None:
        """Mark a message as read if it exists."""
        message = self.db.get(Message, message_id)

        if message is None:
            return None

        message.is_read = True
        self.db.commit()
        self.db.refresh(message)

        return message

    def delete(self, message_id: UUID) -> int:
        """Delete one message by id and return the deleted row count."""
        try:
            deleted_count = self.db.query(Message).filter(
                Message.id == message_id
            ).delete(synchronize_session=False)

            self.db.commit()
            return deleted_count

        except SQLAlchemyError:
            self.db.rollback()
            raise

    def bulk_delete(self, request: MessageBulkDeleteRequest) -> int:
        """Delete multiple messages and return the deleted row count."""
        try:
            deleted_count = self.db.query(Message).filter(
                Message.id.in_(request.message_ids)
            ).delete(synchronize_session=False)

            self.db.commit()
            return deleted_count

        except SQLAlchemyError:
            self.db.rollback()
            raise

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
