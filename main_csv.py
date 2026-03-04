import argparse
import os
import threading
import time
from time import sleep
import requests
import uvicorn

from src.csv_reader import CsvReader
from src.router import ApiRouter
from src.sender import Sender
from src.subscription_registry import SubscriptionRegistry


def main(file: str, interval: float, send_after: int, type: str, port: int, heartbeat_interval : int):
    csv_reader = CsvReader()
    csv_reader.load_data_set(file)

    subscription_registry = SubscriptionRegistry(max_failures=5)

    sender = Sender(csv_reader, subscription_registry, type)
    api = ApiRouter(subscription_registry)

    api_thread = threading.Thread(target=start_api, args=[api, port])
    api_thread.start()
    
    made_progress = threading.Event() #flag to check if main thread is working
    made_progress.set()

    heartbeat_thread = threading.Thread(target=send_heartbeat,args=[made_progress, subscription_registry, heartbeat_interval])
    heartbeat_thread.start()

    last_send: int = int(time.time())
    while True:
        success = sender.prepare_batch()
        if not success:
            print("Sent everything")
            break
        if time.time() - last_send >= send_after:
            sender.send_batch()
            last_send = int(time.time())

        made_progress.set()
        sleep(interval)


def start_api(api: ApiRouter, port: int):
    api.create_routes()
    uvicorn.run(api.app, host="0.0.0.0", port=port)

def send_heartbeat(made_progress : threading.Event , subscription_registry : SubscriptionRegistry, heartbeat_interval : int):
    while True:
        if not made_progress.is_set():
            sleep(heartbeat_interval)
            continue
    
        made_progress.clear()

        for producer in subscription_registry.all_subscribers():
            heartbeat_url = subscription_registry.get_heartbeat_url(producer)
            requests.post(heartbeat_url, data={"status" : "active"})
        
        sleep(heartbeat_interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send CSV lines to API with interval")
    parser.add_argument("-f", "--file", required=True, help="Path to the CSV file")
    parser.add_argument(
        "-i",
        "--interval",
        type=float,
        default=1.0,
        help="Interval between sending lines (seconds)",
    )
    parser.add_argument(
        "-s", "--send", type=int, default=5, help="Interval between batch sends"
    )
    parser.add_argument("-y", "--type", type=str, default="mock", help="Data type")
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=int(os.getenv("PORT", 8000)),
        help="Port of subscription api",
    )
    
    parser.add_argument(
        "-hi", 
        "--heartbeat-interval", 
        type=int, 
        default=int(os.getenv("HEARTBEAT_INTERVAL", 5))
    )

    args = parser.parse_args()

    main(args.file, args.interval, args.send, args.type, args.port, args.heartbeat_interval)
