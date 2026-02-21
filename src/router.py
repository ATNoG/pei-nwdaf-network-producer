import logging
from fastapi import FastAPI
from pydantic import BaseModel

from src.sender import Sender
from src.subscription_registry import SubscriptionRegistry


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SubscriveRequest(BaseModel):
    url : str



class ApiRouter():

    def __init__(self, subscription_registry : SubscriptionRegistry) -> None:
        self.subscription_registry : SubscriptionRegistry = subscription_registry
        self.app = FastAPI()
    
    def create_routes(self):

        @self.app.post("/subscriptions")
        def subscribe(request : SubscriveRequest):
            id = self.subscription_registry.add(request.url)
            return {"subscription_id": id}

        @self.app.delete("/subscriptions/{subscription_id}")
        def unsubscribe(subscription_id : str):
            logger.log(logging.INFO, f"Removing {subscription_id} from subscribers")
            self.subscription_registry.remove(subscription_id)

