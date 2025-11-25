from typing import List
from src.csv_reader import CsvReader
import random
import requests


class Sender():
    def __init__(self, csv_reader:CsvReader ,api_url:str) -> None:
        self.csv_reader:CsvReader = csv_reader
        self.api_url:str = api_url

    def send_line_csv(self, line_num:int) -> None:
        line = self.csv_reader.get_line(line_num)
        self.send_data_to_api(line)

    def send_lines_csv(self, lines_list:List[int]) -> None:
        for line in lines_list:
            self.send_line_csv(line)

    def send_random_line_csv(self) -> None:
        rand = random.randint(0, self.csv_reader.get_how_many_lines() - 1)
        self.send_line_csv(rand)

    def send_random_lines_csv(self, how_many:int) -> None:
        for i in range(how_many):
            self.send_random_line_csv()

    def send_data_to_api(self, data:List[str]) -> None:
        try:
            response = requests.post(
                self.api_url,
                json={"data": data},
                timeout=5
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error sending data to API: {e}")
