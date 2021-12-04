"""
The main data processing goes here (for now).
"""
import datetime

from parse_data import parse_covid_data_file, parse_stock_data_file


class DataManager:
    """TODO

    >>> usa_and_snp = DataManager({'data/stock-snp500.csv', 'data/covid-usa.csv'}, \
                                  datetime.date(2021, 1, 1), datetime.date(2021, 1, 10))
    """
    _covid: dict[str, list[int]]
    _open: dict[str, list[float]]
    _high: dict[str, list[float]]
    _low: dict[str, list[float]]
    _close: dict[str, list[float]]
    _start: datetime.date
    _end: datetime.date
    _duration: int

    def __init__(self, sources: set[str], start: datetime.date, end: datetime.date) -> None:
        """Load the data from the files in sources, only from start to end inclusive.

        Note that we do not explicitly store the date from here on out. It is expected that the
        date in self._<whatever>[i] = start + datetime.timedelta(days=i).

        Preconditions:
            - sources != set()
            - start < end
        """
        self._duration = (end - start).days + 1

        self._covid = {}
        self._open = {}
        self._high = {}
        self._low = {}
        self._close = {}

        for source in sources:
            name = source[11:-4]  # TODO un-hardcode this number

            if 'covid-' in source:
                self._covid[name] = parse_covid_data_file(source, start, end)

                assert len(self._covid[name]) == self._duration
            elif 'stock-' in source:
                dates, *data = parse_stock_data_file(source, start - datetime.timedelta(days=1),
                                                     end)  # TODO ugly-ish

                data = [differentiate_stock_data(x) for x in data]
                dates.pop(0)  # the above implicitly chops off the first element

                data = [fill_stock_data(dates, x, start, end) for x in data]

                self._open[name] = data[0]
                self._high[name] = data[1]
                self._low[name] = data[2]
                self._close[name] = data[3]

                assert len(self._open[name]) == self._duration
                assert len(self._high[name]) == self._duration
                assert len(self._low[name]) == self._duration
                assert len(self._close[name]) == self._duration
            else:
                raise AssertionError('Invalid data type.')


def differentiate_stock_data(data: list[float]) -> list[float]:
    """Convert the prices in the stock data from absolute (cost) to relative
    (change in cost from yesterday).

    Convert the prices in the stock data from absolute (cost) to relative
    (change in cost from yesterday).

    Preconditions:
        - len(data) >= 2

    >>> import math
    >>> expected = [-1.0]
    >>> actual = differentiate_stock_data([1.0, 0.0])
    >>> all(math.isclose(actual[i], expected[i]) for i in range(len(expected)))
    True
    """
    relative_so_far = []

    for i in range(1, len(data)):
        yesterday = data[i - 1]
        today = data[i]
        relative_so_far.append(today - yesterday)

    return relative_so_far


def fill_stock_data(dates: list[datetime.date], data: list[float], start: datetime.date,
                    end: datetime.date) -> list[float]:
    """Fill the given data such that the returned list is equal to the number of days between start
    and end inclusive.  Dates that are not provided in data are assumed to be 0.0 (does not change
    over the weekend).

    Preconditions:
        - len(data) == len(dates)
        - start < end

    >>> fill_stock_data([datetime.date(2021, 1, 2), datetime.date(2021, 1, 4)], \
                        [1.0, 2.0], datetime.date(2021, 1, 1), datetime.date(2021, 1, 4))
    [0.0, 1.0, 0.0, 2.0]
    """
    assert len(data) == len(dates)
    filled_data = [0.0] * ((end - start).days + 1)

    for i in range(len(dates)):
        actual_index = (dates[i] - start).days
        filled_data[actual_index] = data[i]

    return filled_data

# TODO is it safe to make the assumption that there are no gaps in the covid data?  Do we need a
#  fill_covid_data to match fill_stock_data?
