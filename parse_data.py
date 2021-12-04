"""
Get the data from a file, and convert it to the appropriate types from types.py.

This should debatably go in types.py (probably not though).
"""
import csv
import datetime

from records import CovidRecord, StockRecord


def parse_stock_record(row: list[str], stock_name: str) -> StockRecord:
    """Parse the stock data from a row of entries into a StockeRecord object with stock_name.

    Preconditions:
        - stock_name != ''
        - len(row) == 5
    """
    return StockRecord(
        stock=stock_name,
        date=datetime.date.fromisoformat(row[0]),
        open=float(row[1]),
        high=float(row[2]),
        low=float(row[3]),
        close=float(row[4])
    )


def parse_stock_data_file(filename: str, stock_name: str) -> list[StockRecord]:
    """Parse stock data from filename, which contains data from the stock_name stock.
    """
    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # skip the header

        return [parse_stock_record(row, stock_name) for row in reader]


def parse_covid_record(row: list[str]) -> CovidRecord:
    """Parse the stock data from a row of entries into a CovidRecord object.

    Preconditions:
        - len(row) == 3
        - len(row[0]) == 3
    """
    return CovidRecord(
        country=row[0],
        date=datetime.date.fromisoformat(row[1]),
        new_cases=int(row[2])
    )


def parse_covid_data_file(filename: str) -> list[CovidRecord]:
    """Parse covid data from filename.

    It is expected that there will be data from multiple countries in this file.
    """
    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # skip the header

        return [parse_covid_record(row) for row in reader]
