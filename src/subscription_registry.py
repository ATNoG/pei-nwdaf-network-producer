import logging
import threading
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SubscriptionRegistry:
    def __init__(self, max_failures: int = 5):
        self.subscribers: Dict[str, int] = {}
        self.max_failures = max_failures
        self.lock = threading.Lock()

    def add(self, url: str):
        with self.lock: 
            if url not in self.subscribers:
                self.subscribers[url] = 0

    def remove(self, url: str):
        with self.lock:
            self.subscribers.pop(url, None)

    def record_failure(self, url: str):
        with self.lock:
            if url in self.subscribers:
                self.subscribers[url] += 1
                logger.log(logging.INFO, f"{url} took too long to respond")
            
                if self.subscribers[url] >= self.max_failures:
                    self.remove(url)
                    logger.warning(f"{url} didnt respond {self.max_failures} times, assuming it is dead")

    def all_subscribers(self) -> List[str]:
        with self.lock:
            return list(self.subscribers.keys())

