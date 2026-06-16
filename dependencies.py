from fastapi import Depends
from sqlalchemy.orm import Session

from core.database import get_db
from repository.message_repository import MessageRepository
from service.message_service import MessageService


def get_message_service(
    db: Session = Depends(get_db),
) -> MessageService:
    """Create a message service with its repository dependency."""
    repository = MessageRepository(db)
    return MessageService(repository)
