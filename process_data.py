"""
The main data processing goes here (for now).
"""
import datetime

from records import CovidRecord, StockRecord


def differentiate_stock_data(data: list[StockRecord]) -> list[StockRecord]:
    """Convert the prices in the stock data from absolute (cost) to relative
    (change in cost from yesterday).

    Note that the length of the output will be one less than the length of the
    input.

    Preconditions:
        - len(data) >= 2

    >>> yesterday = StockRecord('snp500', datetime.date(2021, 1, 1), 1, 1, 1, 1)
    >>> today = StockRecord('snp500', datetime.date(2021, 1, 2), 1, 0, 2, 1)
    >>> expected = [StockRecord('snp500', datetime.date(2021, 1, 2), 0, -1, 1, 0)]
    >>> actual = differentiate_stock_data([yesterday, today])
    >>> actual == expected
    True
    """
    relative_data_so_far = []

    for i in range(1, len(data)):
        yesterday = data[i - 1]
        today = data[i]
        new_today = StockRecord(
            stock=today.stock,
            date=today.date,
            open=today.open - yesterday.open,
            high=today.high - yesterday.high,
            low=today.low - yesterday.low,
            close=today.close - yesterday.close
        )
        relative_data_so_far.append(new_today)

    return relative_data_so_far
