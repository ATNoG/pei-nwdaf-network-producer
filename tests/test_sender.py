from typing import List
import pytest
from fastapi.testclient import TestClient
from src.sender import Sender
from src.csv_reader import CsvReader
from tests.api_app import mock_app, received_posts


def test_sender_send_random_line(monkeypatch):
    # clear state
    received_posts.clear()

    # Load CSV
    reader = CsvReader()
    reader.load_data_set("dataset/hbahn/cell_data.csv")

    # Mock API
    client = TestClient(mock_app)

    def fake_post(url, json, timeout):
        return client.post(url, json=json)

    # Monkeypatch requests inside sender module
    import src.sender as sender_module
    monkeypatch.setattr(sender_module.requests, "post", fake_post)

    # Create sender
    s = Sender(reader, "http://testserver/data")

    # Act
    s.send_random_line_csv()
    
    print(received_posts)
    # Assert
    assert len(received_posts) == 1
    assert "data" in received_posts[0]
    assert isinstance(received_posts[0]["data"], List)
