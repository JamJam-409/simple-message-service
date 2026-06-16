from uuid import UUID

from app.exceptions import InvalidIndexRangeException, MessageNotFoundException
from app.repository import MessageRepository
from app.schemas import MessageCreateRequest, MessageBulkDeleteRequest, MessageActionResponse, MessageGetResponse


class MessageService:
    """Business logic for message operations."""

    def __init__(self, repository: MessageRepository):
        """Initialize the service with a message repository."""
        self.repository = repository

    def get_unread_messages(self, recipient: str) -> list[MessageGetResponse]:
        """Retrieve unread messages for a recipient."""
        messages = self.repository.get_unread_messages(recipient)
        return [MessageGetResponse.model_validate(message) for message in messages]

    def get_messages_by_index(
        self,
        recipient: str,
        start_index: int,
        stop_index: int | None,
    ) -> list[MessageGetResponse]:
        """Retrieve recipient messages between optional start and stop indexes."""
        if stop_index is not None and stop_index < start_index:
            raise InvalidIndexRangeException()

        messages = self.repository.get_messages_by_index(
            recipient=recipient,
            start_index=start_index,
            stop_index=stop_index,
        )
        return [MessageGetResponse.model_validate(message) for message in messages]

    def create_message(self, request: MessageCreateRequest) -> MessageActionResponse:
        """Create a message and return an action response."""
        self.repository.create(request)
        return MessageActionResponse(message="Message created successfully")

    def delete_message(self, message_id: UUID) -> MessageActionResponse:
        """Delete a message and return an action response."""
        deleted_count = self.repository.delete(message_id)
        if deleted_count == 0:
            raise MessageNotFoundException()

        return MessageActionResponse(message="Message deleted successfully")

    def bulk_delete(self, request: MessageBulkDeleteRequest) -> MessageActionResponse:
        """Delete multiple messages and return an action response."""
        deleted_count = self.repository.bulk_delete(request.message_ids)
        return MessageActionResponse(
            message=f"{deleted_count} of {len(request.message_ids)} messages deleted successfully"
        )
