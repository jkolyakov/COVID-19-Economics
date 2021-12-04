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


def find_stock_spikes(data: list[StockRecord], threshold: float) -> list[tuple[int, str]]:
    """Find spikes in the stock data, data that exceeds threashold.

    Preconditions:
        - data != []

    >>> sample = [StockRecord('snp500', datetime.date(2021, 1, 1), 0, 0, 5, 0), \
                  StockRecord('snp500', datetime.date(2021, 1, 2), 0, 10, 0, 0)]
    >>> find_stock_spikes(sample, 5.0)
    [(1, 'high')]
    """
    spikes_so_far = []

    for i in range(len(data)):
        record = data[i]
        if record.open > threshold:
            spikes_so_far.append((i, 'open'))

        if record.high > threshold:
            spikes_so_far.append((i, 'high'))

        if record.low > threshold:
            spikes_so_far.append((i, 'low'))

        if record.close > threshold:
            spikes_so_far.append((i, 'close'))
        # TODO: This seems needlessly repetitive, is this necessary? Can this be done
        # with metaprogramming?

    return spikes_so_far
    # Open Questions (TODO):
    # - does this algorithm make sense?
    # - should we be returning references rather than indices?
    # - does which field the data comes from actually matter?

    # Something about how the data source is kept feels funky, should we aggregate the stock data
    # into a single file for multiple stock providers, or should we maybe split the countries
    # into separate files.


def find_covid_spikes(data: list[CovidRecord], threshold: float) -> list[int]:
    """Find covid spikes within data.

    Preconditions:
        - data != []

    >>> sample = [CovidRecord('CAN', datetime.date(2021, 1, 1), 5), \
                  CovidRecord('CAN', datetime.date(2021, 1, 2), 6),]
    >>> find_covid_spikes(sample, 5.5)
    [1]
    """
    return [i for i in range(len(data)) if data[i].new_cases > threshold]
    # TODO
    # the fact that this one can be done in one line as a comprehensions, but find_stock_spikes
    # can't is definitely a structural code smell and should be looked into.
