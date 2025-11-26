from typing import Any, Dict, List, Optional, Iterator
import pandas as pd
import math

class CsvReader():

    def __init__(self, chunk_size: int = 10000) -> None:
        self.data_set_path: str = ""
        self.chunk_size: int = chunk_size
        self.separator: str = ";"
        self.headers: Optional[List[str]] = None
        self.current_chunk: Optional[pd.DataFrame] = None
        self.current_chunk_index: int = 0
        self.chunk_iterator: Optional[Iterator[pd.DataFrame]] = None
        self.total_lines: Optional[int] = None


    def load_data_set(self, path: str, separator: str = ";") -> None:
        """Initialize the dataset for chunk-based reading."""
        self.data_set_path = path
        self.separator = separator

        # Read first chunk to get headers
        first_chunk_iter = pd.read_csv(path, sep=separator, chunksize=self.chunk_size)
        first_chunk = next(first_chunk_iter)
        self.headers = first_chunk.columns.tolist()

        # Reset for actual reading
        self._reset_iterator()


    def _reset_iterator(self) -> None:
        """Reset the chunk iterator to the beginning."""
        self.chunk_iterator = pd.read_csv(
            self.data_set_path,
            sep=self.separator,
            chunksize=self.chunk_size
        )
        self.current_chunk = None
        self.current_chunk_index = 0


    def get_headers(self) -> List[str]:
        """Get column headers from the CSV."""
        if self.headers is None:
            raise RuntimeError("Dataset not loaded. Call load_data_set() first.")
        return self.headers


    def get_next_line(self) -> Dict[str, Any]:
        """Get the next line from the CSV, loading chunks as needed."""
        if not self.next_line_exists():
            raise StopIteration("There is no next line")

        # Load next chunk if current chunk is exhausted or not loaded
        if self.current_chunk is None or self.current_chunk_index >= len(self.current_chunk):
            try:
                self.current_chunk = next(self.chunk_iterator)
                self.current_chunk_index = 0
            except StopIteration:
                raise StopIteration("There is no next line")

        # Get the current row
        row = self.current_chunk.iloc[self.current_chunk_index].to_dict()
        self.current_chunk_index += 1

        # Convert all numpy scalars and NaN to native Python types
        row = {
            k: (None if (isinstance(v, float) and math.isnan(v))
                else v.item() if hasattr(v, "item") else v)
            for k, v in row.items()
        }

        return row


    def next_line_exists(self) -> bool:
        """Check if there are more lines to read."""
        # If we have a current chunk with remaining items, return True
        if self.current_chunk is not None and self.current_chunk_index < len(self.current_chunk):
            return True

        # Try to peek at the next chunk
        try:
            if self.chunk_iterator is not None:
                # Save current state
                saved_chunk = self.current_chunk
                saved_index = self.current_chunk_index

                # Try to get next chunk
                self.current_chunk = next(self.chunk_iterator)
                self.current_chunk_index = 0

                # If we got a chunk, return True (chunk is now loaded for next read)
                return True
        except StopIteration:
            return False

        return False


    def get_how_many_lines(self) -> int:
        """
        Get total number of lines in the CSV.
        Warning: This requires iterating through the entire file once.
        The result is cached after the first call.
        """
        if self.total_lines is not None:
            return self.total_lines

        # Count lines by iterating through all chunks
        count = 0
        for chunk in pd.read_csv(self.data_set_path, sep=self.separator, chunksize=self.chunk_size):
            count += len(chunk)

        self.total_lines = count
        return count


    def is_ordered(self, collumn_name: str) -> bool:
        """
        Check if a column is monotonically increasing.
        Warning: This requires iterating through the entire file.
        """
        if collumn_name not in self.get_headers():
            raise ValueError(f"Column {collumn_name} not found in CSV")

        prev_value = None
        for chunk in pd.read_csv(self.data_set_path, sep=self.separator, chunksize=self.chunk_size):
            # Check within chunk
            if not chunk[collumn_name].is_monotonic_increasing:
                return False

            # Check boundary between chunks
            if prev_value is not None:
                first_value = chunk[collumn_name].iloc[0]
                if first_value < prev_value:
                    return False

            # Update previous value for next iteration
            prev_value = chunk[collumn_name].iloc[-1]

        return True
