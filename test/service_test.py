from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.service import MessageService
from app.exceptions import MessageNotFoundException

def make_service(repo_mock=None):
    return MessageService(repo_mock or MagicMock())

# Test delete non-exist message
def test_delete_message_not_found():
    repo = MagicMock()
    repo.delete.return_value = 0
    service = make_service(repo)
    with pytest.raises(MessageNotFoundException):
        service.delete_message(uuid4())


# Test bulk delete with partial failures
def test_bulk_delete_partial_message_found():
    repo = MagicMock()
    repo.delete.return_value = 1
    service = make_service(repo)

    from app.schemas import MessageBulkDeleteRequest
    request: MessageBulkDeleteRequest = MessageBulkDeleteRequest(message_ids=[uuid4(), uuid4()])
    delete_result = service.bulk_delete(request)
    assert "1 of 2" in delete_result.message


# Test
def

