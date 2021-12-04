"""
Get the data from a file, and convert it to the appropriate types from types.py.
"""
import csv
import datetime


def parse_stock_data_file(filename: str, start: datetime.date, end: datetime.date) -> \
        tuple[list[float], list[float], list[float], list[float]]:
    """Parse a stock data file, keeping only the dates within start and end inclusive.
    """
    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # skip the header

        open_so_far = []
        high_so_far = []
        low_so_far = []
        close_so_far = []

        for row in reader:
            date = datetime.date.fromisoformat(row[0])

            if date < start or date > end:  # drop dates that are outside the requested range
                continue

            open_so_far.append(float(row[1]))
            high_so_far.append(float(row[2]))
            low_so_far.append(float(row[3]))
            close_so_far.append(float(row[4]))

        return (open_so_far, high_so_far, low_so_far, close_so_far)


def parse_covid_data_file(filename: str, start: datetime.date, end: datetime.date) -> list[int]:
    """Parse a covid data file, keeping only the dates within start and end inclusive.
    """
    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # skip the header

        cases_so_far = []

        for row in reader:
            date = datetime.date.fromisoformat(row[0])

            if date < start or date > end:  # drop dates that are outside the requested range
                continue

            cases_so_far.append(int(row[1]))

        return cases_so_far
