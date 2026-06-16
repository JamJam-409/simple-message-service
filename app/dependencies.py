from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repository import MessageRepository
from app.service import MessageService


def get_message_service(
    db: Session = Depends(get_db),
) -> MessageService:
    """Create a message service with its repository dependency."""
    repository = MessageRepository(db)
    return MessageService(repository)
