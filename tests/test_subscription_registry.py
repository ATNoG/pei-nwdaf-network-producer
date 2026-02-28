import pytest
from src.subscription_registry import SubscriptionRegistry


@pytest.fixture
def registry() -> SubscriptionRegistry:
    return SubscriptionRegistry(max_failures=3)


def test_add_subscriber(registry: SubscriptionRegistry):
    sub_id = registry.add("http://example.com/hook")
    subscribers = registry.all_subscribers()
    assert sub_id in subscribers
    assert subscribers[sub_id] == "http://example.com/hook"


def test_remove_subscriber(registry: SubscriptionRegistry):
    sub_id = registry.add("http://example.com/hook")
    registry.remove(sub_id)
    assert sub_id not in registry.all_subscribers()


def test_record_failure_auto_evict(registry: SubscriptionRegistry):
    sub_id = registry.add("http://example.com/hook")
    for _ in range(registry.max_failures):
        registry.record_failure(sub_id)
    assert sub_id not in registry.all_subscribers()


def test_record_failure_does_not_evict_before_max(registry: SubscriptionRegistry):
    sub_id = registry.add("http://example.com/hook")
    for _ in range(registry.max_failures - 1):
        registry.record_failure(sub_id)
    assert sub_id in registry.all_subscribers()
