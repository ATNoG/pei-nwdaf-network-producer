from typing import Any, Dict
from src.csv_reader import CsvReader
import requests
import time

class Sender():
    def __init__(self, csv_reader:CsvReader ,api_url:str, id:str="sender", type:str="mock") -> None:
        self.csv_reader:CsvReader = csv_reader
        self.api_url:str = api_url
        self.batch:list = []
        self.id = id
        self.type = type

    def send_next_line(self) -> bool:
        if not self.csv_reader.next_line_exists():
            return False

        line = self.csv_reader.get_next_line()

        self.send_line_to_api(line)
        return True

    def prepare_batch(self)->bool:
        if not self.csv_reader.next_line_exists():
            return False

        line = self.csv_reader.get_next_line()
        toAdd = {
            "analyticsMetadata": line,
            "timestamp":int(time.time())
        }
        self.batch.append(toAdd)
        return True

    def send_batch(self) -> None:
        if not self.batch:
            return  # nothing to send

        # Attach a timestamp for the batch itself
        payload = {
            "analyticsData": self.batch,
            "producerId":self.id,
            "eventId":self.type,
        }
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=5
            )
            response.raise_for_status()
            print(f"Sent batch of {len(self.batch)} lines successfully")
        except requests.RequestException as e:
            print(f"Error sending batch to API: {e}")

        # Clear the batch after sending
        self.batch = []



    def send_line_to_api(self, line:Dict[str, Any]) -> None:
        try:
            response = requests.post(
                self.api_url,
                json={"data": line,
                    "timestamp": int(time.time())},
                timeout=5
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error sending data to API: {e}")
