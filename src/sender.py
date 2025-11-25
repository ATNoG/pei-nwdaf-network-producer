from typing import Any, Dict
from csv_reader import CsvReader
import requests


class Sender():
    def __init__(self, csv_reader:CsvReader ,api_url:str) -> None:
        self.csv_reader:CsvReader = csv_reader
        self.api_url:str = api_url

    
    def send_next_line(self) -> bool:
        if not self.csv_reader.next_line_exists():
            return False
        
        line = self.csv_reader.get_next_line()
        self.send_line_to_api(line)
        return True


    def send_line_to_api(self, line:Dict[str, Any]) -> None:
        try:
            response = requests.post(
                self.api_url,
                json={"data": line},
                timeout=5
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error sending data to API: {e}")
