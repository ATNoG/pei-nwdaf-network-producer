import pytest

from src.csv_reader import CsvReader

@pytest.fixture
def csv_reader() -> CsvReader:
    csv_reader = CsvReader()
    csv_reader.load_data_set("tests/test.csv")
    return csv_reader

def test_ordered_with_ordered_collumn(csv_reader : CsvReader):
    assert csv_reader.is_ordered("collumn1")

def test_ordered_with_unordered_collumn(csv_reader : CsvReader):
    assert not csv_reader.is_ordered("collumn2")

def test_ordered_with_collumn_that_doesnt_exist(csv_reader : CsvReader):
    with pytest.raises(ValueError):
        csv_reader.is_ordered("not_a_column")

def test_get_next_line(csv_reader : CsvReader):
    assert csv_reader.get_next_line() == {"collumn1" : 1, "collumn2" : 3, "collumn3" : 1}
    assert csv_reader.get_next_line() == {"collumn1" : 2, "collumn2" : 1, "collumn3" : 1}
    assert csv_reader.get_next_line() == {"collumn1" : 4, "collumn2" : 2, "collumn3" : 1}
    assert csv_reader.get_next_line() == {"collumn1" : 5, "collumn2" : 2, "collumn3" : 1}

    with pytest.raises(StopIteration):
        csv_reader.get_next_line()

