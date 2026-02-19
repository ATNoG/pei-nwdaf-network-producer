from logging import Logger
from typing import Dict, List

class SubscriptionRegistry:
    def __init__(self, max_failures: int = 5):
        self.subscribers: Dict[str, int] = {}
        self.max_failures = max_failures

    def add(self, url: str):
        if url not in self.subscribers:
            self.subscribers[url] = 0

    def remove(self, url: str):
        self.subscribers.pop(url, None)

    def record_failure(self, url: str):
        if url in self.subscribers:
            self.subscribers[url] += 1
            Logger.log("%s took too long to respond", url)
            
            if self.subscribers[url] >= self.max_failures:
                self.remove(url)
                Logger.log("%s didnt respond %d times, assuming it is dead", self.max_failures, url)

    def all_subscribers(self) -> List[str]:
        return list(self.subscribers.keys())

