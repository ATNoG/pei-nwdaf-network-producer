import argparse
from time import sleep
from src.sender import Sender
from src.csv_reader import CsvReader
import time

def main(file: str, interval: float, api_url: str, send_after:int, type:str):
    csv_reader = CsvReader()
    csv_reader.load_data_set(file)
    sender = Sender(csv_reader, api_url, type)

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

    args = parser.parse_args()

    main(args.file, args.interval, args.api, args.send, args.type)
