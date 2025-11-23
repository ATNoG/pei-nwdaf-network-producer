from typing import List
import pandas as pd

class CsvReader():

    def __init__(self) -> None:
        self.data_set_path : str
        self.csv : pd.DataFrame

    def load_data_set(self, path : str) -> None:
        self.data_set_path = path
        self.csv = pd.read_csv(path)

    def get_headers(self) -> List[str]:
        return self.csv.columns.tolist()

    def get_line(self, n : int) -> List[str]:
        return self.csv.iloc[n].tolist()

    def get_lines(self, list_n : List[int]) -> List[List[str]]:
        list_lines = []
        for n in list_n:
            list_lines.append(self.get_line(n))
        return list_lines
    
    def get_how_many_lines(self) -> int:
        #this doesnt include the headers
        return len(self.csv)
