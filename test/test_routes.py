from uuid import uuid4


class TestCreateMessage:
    def test_create_returns_201(self, client):
        resp = client.post("/messages/", json={
            "sender": "alice",
            "recipient": "bob",
            "content": "hello",
        })
        assert resp.status_code == 201

    def test_create_missing_field_returns_422(self, client):
        resp = client.post("/messages/", json={
            "sender": "alice",
        })
        assert resp.status_code == 422

    def test_create_empty_content_returns_422(self, client):
        resp = client.post("/messages/", json={
            "sender": "alice",
            "recipient": "bob",
            "content": "",
        })
        assert resp.status_code == 422


class TestGetUnreadMessages:
    def test_fetch_unread_returns_messages(self, client):
        client.post("/messages/", json={
            "sender": "alice", "recipient": "bob", "content": "msg1",
        })
        client.post("/messages/", json={
            "sender": "alice", "recipient": "bob", "content": "msg2",
        })

        resp = client.get("/messages/bob/unread")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_fetch_unread_marks_as_read(self, client):
        client.post("/messages/", json={
            "sender": "alice", "recipient": "bob", "content": "hello",
        })

        client.get("/messages/bob/unread")
        resp = client.get("/messages/bob/unread")

        assert resp.json() == []

    def test_fetch_unread_only_returns_recipients_messages(self, client):
        client.post("/messages/", json={
            "sender": "alice", "recipient": "bob", "content": "for bob",
        })
        client.post("/messages/", json={
            "sender": "alice", "recipient": "charlie", "content": "for charlie",
        })

        resp = client.get("/messages/bob/unread")
        assert len(resp.json()) == 1
        assert resp.json()[0]["content"] == "for bob"

    def test_recipient_is_case_insensitive(self, client):
        client.post("/messages/", json={
            "sender": "Alice", "recipient": "Bob", "content": "hi",
        })

        resp = client.get("/messages/bob/unread")
        assert len(resp.json()) == 1


class TestGetMessagesByIndex:
    def test_returns_messages_ordered_by_time(self, client):
        for i in range(5):
            client.post("/messages/", json={
                "sender": "alice", "recipient": "bob", "content": f"msg{i}",
            })

        resp = client.get("/messages/bob", params={"start_index": 0, "stop_index": 5})
        messages = resp.json()
        assert len(messages) == 5
        assert messages[0]["content"] == "msg0"
        assert messages[4]["content"] == "msg4"

    def test_start_and_stop_slices_correctly(self, client):
        for i in range(5):
            client.post("/messages/", json={
                "sender": "alice", "recipient": "bob", "content": f"msg{i}",
            })

        resp = client.get("/messages/bob", params={"start_index": 1, "stop_index": 3})
        messages = resp.json()
        assert len(messages) == 2
        assert messages[0]["content"] == "msg1"
        assert messages[1]["content"] == "msg2"

    def test_no_stop_index_returns_all_from_start(self, client):
        for i in range(3):
            client.post("/messages/", json={
                "sender": "alice", "recipient": "bob", "content": f"msg{i}",
            })

        resp = client.get("/messages/bob", params={"start_index": 1})
        assert len(resp.json()) == 2

    def test_includes_previously_read_messages(self, client):
        client.post("/messages/", json={
            "sender": "alice", "recipient": "bob", "content": "hello",
        })
        client.get("/messages/bob/unread")  # marks as read

        resp = client.get("/messages/bob", params={"start_index": 0})
        assert len(resp.json()) == 1
        assert resp.json()[0]["is_read"] is True

    def test_invalid_range_returns_400(self, client):
        resp = client.get("/messages/bob", params={"start_index": 5, "stop_index": 2})
        assert resp.status_code == 400


class TestDeleteMessage:
    def test_delete_existing_returns_204(self, client):
        client.post("/messages/", json={
            "sender": "alice", "recipient": "bob", "content": "hello",
        })
        messages = client.get("/messages/bob/unread").json()
        msg_id = messages[0]["id"]

        resp = client.delete(f"/messages/{msg_id}")
        assert resp.status_code == 204

    def test_deleted_message_not_in_results(self, client):
        client.post("/messages/", json={
            "sender": "alice", "recipient": "bob", "content": "hello",
        })
        messages = client.get("/messages/bob", params={"start_index": 0}).json()
        msg_id = messages[0]["id"]

        client.delete(f"/messages/{msg_id}")
        resp = client.get("/messages/bob", params={"start_index": 0})
        assert resp.json() == []

    def test_delete_nonexistent_returns_204(self, client):
        resp = client.delete(f"/messages/{uuid4()}")
        assert resp.status_code == 204


class TestBulkDelete:
    def test_bulk_delete_removes_messages(self, client):
        for i in range(3):
            client.post("/messages/", json={
                "sender": "alice", "recipient": "bob", "content": f"msg{i}",
            })
        messages = client.get("/messages/bob", params={"start_index": 0}).json()
        ids = [m["id"] for m in messages]

        resp = client.request("DELETE", "/messages/", json={"message_ids": ids})
        assert resp.status_code == 200
        assert "3 of 3" in resp.json()["message"]

        remaining = client.get("/messages/bob", params={"start_index": 0}).json()
        assert remaining == []

    def test_bulk_delete_partial(self, client):
        client.post("/messages/", json={
            "sender": "alice", "recipient": "bob", "content": "hello",
        })
        messages = client.get("/messages/bob", params={"start_index": 0}).json()
        real_id = messages[0]["id"]

        resp = client.request("DELETE", "/messages/", json={
            "message_ids": [real_id, str(uuid4())],
        })
        assert "1 of 2" in resp.json()["message"]
