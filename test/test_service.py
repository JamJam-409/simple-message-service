from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.exceptions import InvalidIndexRangeException
from app.schemas import MessageBulkDeleteRequest, MessageCreateRequest
from app.service import MessageService


def make_service(repo_mock=None):
    return MessageService(repo_mock or MagicMock())


def make_message_mock(sender="alice", recipient="bob", content="hello"):
    msg = MagicMock()
    msg.id = uuid4()
    msg.sender = sender
    msg.recipient = recipient
    msg.content = content
    msg.is_read = False
    msg.created_at = datetime.now(timezone.utc)
    return msg


class TestCreateMessage:
    def test_calls_repository_create(self):
        repo = MagicMock()
        service = make_service(repo)
        request = MessageCreateRequest(sender="alice", recipient="bob", content="hi")

        service.create_message(request)

        repo.create.assert_called_once_with(request)

    def test_returns_201_response(self):
        service = make_service()
        request = MessageCreateRequest(sender="alice", recipient="bob", content="hi")

        result = service.create_message(request)

        assert result.status_code == 201


class TestGetUnreadMessages:
    def test_returns_empty_when_no_messages(self):
        repo = MagicMock()
        repo.get_unread_messages.return_value = []
        service = make_service(repo)

        result = service.get_unread_messages("bob")

        assert result == []

    def test_returns_validated_messages(self):
        repo = MagicMock()
        msg = make_message_mock()
        repo.get_unread_messages.return_value = [msg]
        service = make_service(repo)

        result = service.get_unread_messages("bob")

        assert len(result) == 1
        assert result[0].content == "hello"
        assert result[0].sender == "alice"

    def test_calls_repository_with_recipient(self):
        repo = MagicMock()
        repo.get_unread_messages.return_value = []
        service = make_service(repo)

        service.get_unread_messages("bob")

        repo.get_unread_messages.assert_called_once_with("bob")


class TestGetMessagesByIndex:
    def test_valid_range_calls_repository(self):
        repo = MagicMock()
        repo.get_messages_by_index.return_value = []
        service = make_service(repo)

        service.get_messages_by_index("bob", start_index=0, stop_index=5)

        repo.get_messages_by_index.assert_called_once_with(
            recipient="bob", start_index=0, stop_index=5
        )

    def test_stop_less_than_start_raises(self):
        service = make_service()

        with pytest.raises(InvalidIndexRangeException):
            service.get_messages_by_index("bob", start_index=10, stop_index=5)

    def test_none_stop_index_is_valid(self):
        repo = MagicMock()
        repo.get_messages_by_index.return_value = []
        service = make_service(repo)

        service.get_messages_by_index("bob", start_index=0, stop_index=None)

        repo.get_messages_by_index.assert_called_once_with(
            recipient="bob", start_index=0, stop_index=None
        )

    def test_equal_start_and_stop_is_valid(self):
        repo = MagicMock()
        repo.get_messages_by_index.return_value = []
        service = make_service(repo)

        service.get_messages_by_index("bob", start_index=5, stop_index=5)

        repo.get_messages_by_index.assert_called_once()


class TestDeleteMessage:
    def test_returns_204_response(self):
        repo = MagicMock()
        repo.delete.return_value = 1
        service = make_service(repo)

        result = service.delete_message(uuid4())

        assert result.status_code == 204

    def test_calls_repository_with_id(self):
        repo = MagicMock()
        repo.delete.return_value = 1
        service = make_service(repo)
        msg_id = uuid4()

        service.delete_message(msg_id)

        repo.delete.assert_called_once_with(msg_id)


class TestBulkDelete:
    def test_all_deleted(self):
        repo = MagicMock()
        repo.bulk_delete.return_value = 3
        service = make_service(repo)
        request = MessageBulkDeleteRequest(message_ids=[uuid4(), uuid4(), uuid4()])

        result = service.bulk_delete(request)

        assert "3 of 3" in result.message

    def test_partial_delete(self):
        repo = MagicMock()
        repo.bulk_delete.return_value = 1
        service = make_service(repo)
        request = MessageBulkDeleteRequest(message_ids=[uuid4(), uuid4()])

        result = service.bulk_delete(request)

        assert "1 of 2" in result.message

    def test_none_deleted(self):
        repo = MagicMock()
        repo.bulk_delete.return_value = 0
        service = make_service(repo)
        request = MessageBulkDeleteRequest(message_ids=[uuid4(), uuid4()])

        result = service.bulk_delete(request)

        assert "0 of 2" in result.message
