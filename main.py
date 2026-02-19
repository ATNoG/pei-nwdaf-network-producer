import argparse
import uvicorn
import threading
from time import sleep
from src.router import ApiRouter
from src.sender import Sender
from src.csv_reader import CsvReader
import time

from src.subscription_registry import SubscriptionRegistry

def main(file: str, interval: float, api_url: str, send_after:int, type:str, port:int):
    csv_reader = CsvReader()
    csv_reader.load_data_set(file)

    subscription_registry = SubscriptionRegistry(max_failures=5)

    sender = Sender(csv_reader, subscription_registry, type)
    api = ApiRouter(subscription_registry)
    
    api_thread = threading.Thread(target=start_api, args=[api, port])
    api_thread.start()

    last_send:int = int(time.time())
    while True:
        success = sender.prepare_batch()
        if not success:
            print("Sent everything")
            break
        if time.time() - last_send >= send_after:
            sender.send_batch()
            last_send = int(time.time())

        sleep(interval)

def start_api(api : ApiRouter, port : int):
    api.create_routes()
    uvicorn.run(api.app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send CSV lines to API with interval")
    parser.add_argument("-f", "--file", required=True, help="Path to the CSV file")
    parser.add_argument("-i", "--interval", type=float, default=1.0, help="Interval between sending lines (seconds)")
    parser.add_argument("-a", "--api", type=str, default="https://webhook.site/d2c1b083-911c-435e-89f4-48467917c345",
                        help="API URL to send data to")
    parser.add_argument("-s", "--send", type=str, default=5,
                        help="Interval between batch sends")
    parser.add_argument("-y", "--type", type=str, default="mock",
                        help="Data type")
    parser.add_argument("-p", "--port", type=int, default=8000, help="Port of subscription api")

    args = parser.parse_args()

    main(args.file, args.interval, args.api, args.send, args.type, args.port)
