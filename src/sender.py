from typing import List
from csv_reader import CsvReader
import random



class Sender():
    def __init__(self) -> None:
        self.csv_path:str
        self.csv_reader:CsvReader = CsvReader()

    def load_csv(self, path:str) -> None:
        self.csv_reader.load_data_set(path)

    def send_line_csv(self, line_num:int) -> None:
        line = self.csv_reader.get_line(line_num)

    def send_lines_csv(self, lines_list:List[int]) -> None:
        for line in lines_list:
            self.send_line_csv(line)

    def send_random_line_csv(self) -> None:
        rand = random.randint(0, self.csv_reader.get_how_many_lines())
        self.send_line_csv(rand)

    def send_random_lines_csv(self, how_many:int) -> None:
        for i in range(how_many):
            self.send_random_line_csv()
