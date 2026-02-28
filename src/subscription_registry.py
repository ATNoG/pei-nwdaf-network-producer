import logging
import threading
import uuid
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SubscriptionRegistry:
    def __init__(self, max_failures: int = 5):
        self.subscribers: Dict[str, str] = {}
        self.subs_failures : Dict[str, int] = {}
        self.max_failures = max_failures
        self.lock = threading.Lock()

    def add(self, url: str):
        subscription_id = str(uuid.uuid4())
        with self.lock: 
            self.subscribers[subscription_id] = url
            self.subs_failures[subscription_id] = 0
        return subscription_id

    def remove(self, sub_id: str):
        with self.lock:
            self.subscribers.pop(sub_id, None)
            self.subs_failures.pop(sub_id, None)

    def record_failure(self, id: str):
        with self.lock:
            if id in self.subs_failures:
                self.subs_failures[id] += 1
                logger.log(logging.INFO, f"Subscription with id:{id} took too long to respond")
            
                if self.subs_failures[id] >= self.max_failures:
                    self.subscribers.pop(id, None)
                    self.subs_failures.pop(id, None)

                    logger.warning(f"{id} didnt respond {self.max_failures} times, assuming it is dead")

    def all_subscribers(self) -> Dict[str, str]:
        with self.lock:
            return self.subscribers.copy()

    def get_url(self, id : str) -> str:
        with self.lock:
            return self.subscribers[id]
