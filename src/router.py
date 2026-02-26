import logging
from fastapi import FastAPI, HTTPException
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
            try:
                self.subscription_registry.remove(subscription_id)
                return ({"success" : True}, 200)
            except KeyError:
                logger.warning(f"Subscription {subscription_id} not found")
                raise HTTPException(status_code=404, detail="Subscription not found")
            except Exception as e:
                logger.error(f"Failed to remove subscription {subscription_id}: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")



