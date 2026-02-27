from typing import Dict
import pytest
from fastapi.testclient import TestClient
from requests import RequestException
from src.sender import Sender
from src.csv_reader import CsvReader
from src.subscription_registry import SubscriptionRegistry
from tests.api_app import mock_app, received_posts


@pytest.fixture
def csv_reader() -> CsvReader:
    reader = CsvReader()
    reader.load_data_set("tests/test.csv")
    return reader


@pytest.fixture
def registry() -> SubscriptionRegistry:
    return SubscriptionRegistry(max_failures=3)


def test_send_batch_fans_out_to_all_subscribers(monkeypatch, csv_reader, registry):
    received_posts.clear()

    client = TestClient(mock_app)

    def fake_post(url, json, timeout):
        return client.post("/data", json=json)

    import src.sender as sender_module

    monkeypatch.setattr(sender_module.requests, "post", fake_post)

    registry.add("http://testserver/data")
    registry.add("http://testserver/data")

    sender = Sender(csv_reader, registry, type="mock")
    sender.prepare_batch()
    sender.send_batch()

    # Both subscribers should have received the batch
    assert len(received_posts) == 2
    assert "analyticsData" in received_posts[0]
    assert "analyticsData" in received_posts[1]


def test_send_batch_records_failure_on_error(monkeypatch, csv_reader, registry):
    def fake_post_error(url, json, timeout):
        raise RequestException("connection refused")

    import src.sender as sender_module

    monkeypatch.setattr(sender_module.requests, "post", fake_post_error)

    sub_id = registry.add("http://unreachable/hook")

    sender = Sender(csv_reader, registry, type="mock")
    sender.prepare_batch()
    sender.send_batch()

    assert registry.subs_failures.get(sub_id, 0) == 1


def test_send_batch_auto_evicts_failing_subscriber(monkeypatch, csv_reader, registry):
    def fake_post_error(url, json, timeout):
        raise RequestException("connection refused")

    import src.sender as sender_module

    monkeypatch.setattr(sender_module.requests, "post", fake_post_error)

    sub_id = registry.add("http://unreachable/hook")

    sender = Sender(csv_reader, registry, type="mock")

    for _ in range(registry.max_failures):
        csv_reader_inner = CsvReader()
        csv_reader_inner.load_data_set("tests/test.csv")
        sender.csv_reader = csv_reader_inner
        sender.prepare_batch()
        sender.send_batch()

    assert sub_id not in registry.all_subscribers()
