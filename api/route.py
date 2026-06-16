from uuid import UUID

from fastapi import APIRouter, Depends, Query

from dependencies import get_message_service
from schemas.message_action_response import MessageActionResponse
from schemas.message_bulk_delete_request import MessageBulkDeleteRequest
from schemas.message_create_request import MessageCreateRequest
from schemas.message_get_response import MessageGetResponse
from service.message_service import MessageService

router = APIRouter(
    prefix="/messages",
    tags=["messages"]
)


@router.get("/", response_model=list[MessageGetResponse])
def get_messages(service: MessageService = Depends(get_message_service)):
    """Return all messages."""
    return service.get_messages()


@router.post("/", response_model=MessageActionResponse)
def create_message(
    request: MessageCreateRequest,
    service: MessageService = Depends(get_message_service),
):
    """Create a new message."""
    return service.create_message(request)


@router.get("/unread", response_model=list[MessageGetResponse])
def get_unread_messages(
    recipient: str,
    service: MessageService = Depends(get_message_service),
):
    """Return unread messages for a recipient."""
    return service.get_unread_messages(recipient)


@router.get("/by-index", response_model=list[MessageGetResponse])
def get_messages_by_index(
    recipient: str,
    start_index: int = Query(0, description="Start index", ge=0),
    stop_index: int | None = Query(None, description="End index", ge=0),
    service: MessageService = Depends(get_message_service),
):
    """Return recipient messages between optional start and stop indexes."""
    return service.get_messages_by_index(
        recipient=recipient,
        start_index=start_index,
        stop_index=stop_index,
    )


@router.delete("/bulk", response_model=MessageActionResponse)
def bulk_delete(
    request: MessageBulkDeleteRequest,
    service: MessageService = Depends(get_message_service),
):
    """Delete multiple messages by id."""
    return service.bulk_delete(request)


@router.delete("/{message_id}", response_model=MessageActionResponse)
def delete_message(
    message_id: UUID,
    service: MessageService = Depends(get_message_service),
):
    """Delete one message by id."""
    return service.delete_message(message_id)

