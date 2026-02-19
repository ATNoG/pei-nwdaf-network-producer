from logging import Logger
from fastapi import FastAPI
from pydantic import BaseModel

from src.sender import Sender
from src.subscription_registry import SubscriptionRegistry


class SubscriveRequest(BaseModel):
    url : str


class UnsubscriveRequest(BaseModel):
    url : str

class ApiRouter():

    def __init__(self, subscription_registry : SubscriptionRegistry) -> None:
        self.subscription_registry : SubscriptionRegistry = subscription_registry
        self.app = FastAPI()
    
    def create_routes(self):

        @self.app.post("/subscribe")
        def subscribe(request : SubscriveRequest):
            self.subscription_registry.add(request.url)
            return {"message": f"{request.url} subscribed successfully"}

        @self.app.delete("/unsubscribe")
        def unsubscribe(request : UnsubscriveRequest):
            Logger.log("Removing %s from subscribers", request.url)
            self.subscription_registry.remove(request.url)

