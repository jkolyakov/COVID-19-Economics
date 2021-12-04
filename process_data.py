"""
The main data processing goes here (for now).
"""
import datetime

from parse_data import parse_covid_data_file, parse_stock_data_file


class DataManager:
    """TODO
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
            name = source[11:-4]

            if 'covid-' in source:
                self._covid[name] = parse_covid_data_file(source, start, end)

                assert len(self._covid[name]) == self._duration
            elif 'stock-' in source:
                absolute_data = parse_stock_data_file(source, start - datetime.timedelta(days=1),
                                                      end)
                data = tuple(differentiate_stock_data(x) for x in absolute_data)
                self._open[name] = data[0]
                self._high[name] = data[1]
                self._low[name] = data[2]
                self._close[name] = data[3]

                # assert len(self._open[name]) == self._duration
                # assert len(self._high[name]) == self._duration
                # assert len(self._low[name]) == self._duration
                # assert len(self._close[name]) == self._duration
                # these assertions don't make sense because of weekends :(
                # TODO need to actually consider dates, darn
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
