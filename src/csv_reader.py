from typing import Any, Dict, List
import pandas as pd
import math

class CsvReader():

    def __init__(self) -> None:
        self.data_set_path : str
        self.csv : pd.DataFrame
        self.current_line : int
    

    def load_data_set(self, path : str, separator=";") -> None:
        self.data_set_path = path
        self.csv = pd.read_csv(path, sep=separator)
        self.current_line = 0

    
    def get_headers(self) -> List[str]:
        return self.csv.columns.tolist()

    
    def get_line(self, n : int) -> Dict[str, Any]:
        if n >= self.get_how_many_lines():
            raise ValueError("Cant index a line that doesnt exist")
        
        row = self.csv.iloc[n].to_dict()
        
        # convert all numpy scalars, and NaN to native Python types
        row = {
        k: (None if (isinstance(v, float) and math.isnan(v)) else v.item() if hasattr(v, "item") else v)
        for k, v in row.items()
        }

        return row

    
    def get_lines(self, list_n : List[int]) -> List[Dict[str,Any]]:
        list_lines = []
        for n in list_n:
            list_lines.append(self.get_line(n))
        return list_lines
    

    def get_next_line(self) -> Dict[str, Any]:
        if not self.next_line_exists():
            raise StopIteration("There is no next line")
        line = self.get_line(self.current_line)
        self.current_line += 1
        return line
    
    
    def next_line_exists(self) -> bool:
        return self.current_line < self.get_how_many_lines()


    def get_how_many_lines(self) -> int:
        #this doesnt include the headers
        return len(self.csv)

    def is_ordered(self, collumn_name : str) -> bool:
        if not collumn_name in self.get_headers():
            raise ValueError(f"Column {collumn_name} not found in CSV") 
        return self.csv[collumn_name].is_monotonic_increasing
        
