"""
The main data processing goes here (for now).
"""
import datetime
from typing import Union

import pandas as pd

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

        Note that we do not explicitly store the date from here on out. It is assumed that the
        date in self._<whatever>[i] = _index_to_date. TODO remove this note before final submission

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
                dates, data = parse_covid_data_file(source, start, end)
                self._covid[name] = fill_covid_data(dates, data, start, end)

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

    def _index_to_date(self, index: int) -> datetime.date:
        """Convert the index of an element in one of the many lists that this class contains into
        its canonical date.

        Preconditions:
            - self.index < self._duration

        >>> # TODO
        """
        return self._start + datetime.timedelta(days=index)

    def get_global_statistics(self) -> list[float]:
        """TODO: what parameters should this interface take?
        """
        pass

    def get_local_statistics(self) -> list[float]:
        """TODO: what parameters should this interface take?
        """
        pass


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
        - TODO there are way more preconditions

    >>> fill_stock_data([datetime.date(2021, 1, 2), datetime.date(2021, 1, 4)], \
                        [1.0, 2.0], datetime.date(2021, 1, 1), datetime.date(2021, 1, 4))
    [0.0, 1.0, 0.0, 2.0]
    """
    filled_data = [0.0] * ((end - start).days + 1)
    fill_data(dates, data, filled_data, start)
    return filled_data


def fill_covid_data(dates: list[datetime.date], data: list[int], start: datetime.date,
                    end: datetime.date) -> list[int]:
    """Fill the given data such that the returned list is equal to the number of days between start
    and end inclusive.  Dates that are not provided in data are assumed to be 0 (this does mean
    that we conflate no data with 0 new cases, which is ok for our purposes).

    Preconditions:
        - len(data) == len(dates)
        - start < end
        - TODO there are way more preconditions

    >>> fill_covid_data([datetime.date(2021, 1, 2), datetime.date(2021, 1, 4)], \
                        [1, 2], datetime.date(2021, 1, 1), datetime.date(2021, 1, 4))
    [0, 1, 0, 2]
    """
    filled_data = [0] * ((end - start).days + 1)
    fill_data(dates, data, filled_data, start, )
    return filled_data


def fill_data(dates: list[datetime.date], data: list[Union[int, float]],
              base: list[Union[int, float]], start: datetime.date) -> None:
    """Backend function for fill_covid_data and fill_stock_data.  Actually performs the copy in a
    type agnostic way.

    Preconditions:
        - len(data) == len(dates)
        - start < end
        - TODO there are way more preconditions

    >>> # TODO
    """
    for i in range(len(dates)):
        actual_index = (dates[i] - start).days
        base[actual_index] = data[i]


def spike_determiner(stock: list[float], covid: list[float], threshold: int) -> list[int]:
    """Checks to see what time periods count as spikes in both stock price and covid numbers
     and returns those indices with a threshold of 1 day.

    Preconditions:
        - len(stock) == len(covid)
    >>> TODO

    """
    spikes = []
    for x in range(len(stock) - 1):
        if abs(stock[x+1]) >= 75 and covid[x] >= threshold:
            spikes.append(x)
    return spikes


def matching_spikes(covid: list[float], stock: list[float], threshold: int) \
        -> list[list[int], list[int]]:
    """Matching the day of the first time covid broke the threshold with the first day of
    the first stock spike. Will return list with the covid spike indices lined up with the
    correlating stock spike indices.

    Preconditions:
        - len(stock) == len(covid)

    >>> TODO
    """
    final_data = [[], []]
    spikes = spike_determiner(stock, covid, threshold)
    for x in spikes:
        final_data[0][0].append(covid[x])
        final_data[0][1].append(stock[x + 1])
    return final_data


def convert_data(covid: list[float], stock: list[float]) -> list[tuple]:
    """Converts spike data into form that will be accepted by the Panda's library DataFrame class

    Preconditions:
        - len(covid) == len(stock)
    >>> convert_data([0.2 , 0.0, 0.6, 0.2], [0.3, 0.6, 0.0, 0.1])
    [(0.2, 0.3), (0.0, 0.6), (0.6, 0.0), (0.2, 0.1)]
    """
    final_data = []
    for i in range(len(covid)):
        final_data.append((covid[i], stock[i]))
    return final_data


def return_correlation_coefficient(covid: list[float], stock: list[float]) -> float:
    """Returns correlation matrix from the data
    >>> import math
    >>> c = return_correlation_coefficient([0.2 , 0.0, 0.6, 0.2], [0.3, 0.6, 0.0, 0.1])
    >>> math.isclose(-0.8510644963469901, c)
    True
    """
    data = convert_data(covid, stock)
    df = pd.DataFrame(data, columns=['covid', 'stocks'])
    correlation = df.corr()
    return correlation['covid']['stocks']
