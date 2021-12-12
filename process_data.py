"""
The main data processing goes here (for now).
"""
import datetime
from typing import Union

import pandas as pd

from parse_data import parse_covid_data_file, parse_stock_data_file


class DataManager:
    """Data manager class that will both store and handle processing data from the CSV files
    into a form that can be used by the Pandas library to calculate a correlation coefficient.
    TODO: Check if this is OK

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
        self._start = start
        self._end = end

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

        >>> usa_and_snp = DataManager({'data/stock-snp500.csv', 'data/covid-usa.csv'}, \
                                  datetime.date(2021, 1, 1), datetime.date(2021, 3, 1))
        >>> usa_and_snp._index_to_date(5)
        datetime.date(2021, 1, 6)
        """
        return self._start + datetime.timedelta(days=index)

    def get_weekly_global_statistics(self, stock_stream: str, days: int, stock: str,
                                     country: str) -> list[float]:
        """Output a list of weekly correlation coefficients derived from the stock_stream data for
        stock compared against the covid data of country.
        TODO: Write out logic in the graph that is being created from this data

        Preconditions:
            - stock_stream in {'high', 'low', 'open', 'close'}
            - days > 0
            - stock in self._open
            - country in self._covid
            - all(len(self._covid[x]) > 2 for x in self._covid)
            - all(len(self._high[x]) > 2 for x in self._high)
            - all(len(self._low[x]) > 2 for x in self._low)
            - all(len(self._open[x]) > 2 for x in self._open)
            - all(len(self._close[x]) > 2 for x in self._close)

        >>> # TODO
        # TODO: check if lack of data causes error
        """
        corr_data = []
        covid_data = self._covid[country][days:]
        final_corr: list[float]
        if days != 0:
            if stock_stream == 'high':
                stock_data = self._high[stock][:-days]
            elif stock_stream == 'low':
                stock_data = self._low[stock][:-days]
            elif stock_stream == 'open':
                stock_data = self._open[stock][:-days]
            else:
                stock_data = self._close[stock][:-days]
        else:
            if stock_stream == 'high':
                stock_data = self._high[stock]
            elif stock_stream == 'low':
                stock_data = self._low[stock]
            elif stock_stream == 'open':
                stock_data = self._open[stock]
            else:
                stock_data = self._close[stock]
        for x in range(0, len(covid_data) - 6, 7):
            if x + 7 < len(covid_data):
                corr_data.append(return_correlation_coefficient(covid_data[x:x + 7],
                                                                stock_data[x:x + 7]))
            else:
                corr_data.append(return_correlation_coefficient(covid_data[x:], stock_data[x:]))
        # Replaces all NotANumber values with 0.0. This is okay and will not change the final
        # results as those values occur when no new covid cases occur all week, which is equivalent
        # to saying covid cases had no correlation to the fluctuation in stock price.
        # FIXME: Check comment and whether we actually want to go with 0.0 to fill the nan values
        final_corr = [0.0 if pd.isna(y) else y for y in corr_data]
        return final_corr

    def get_weekly_local_statistics(self, stock_stream: str, stock: str,
                                    country: str, threshold: int) -> float:
        """ Filters the data for matching spikes and returns a list of weekly correlation
        coefficients.
        TODO: Write out logic in the graph that is being created from this data

        Preconditions:
            - stock_stream in {'high', 'low', 'open', 'close'}
            - stock in self._open
            - country in self._covid
            - all(len(self._covid[x]) > 2 for x in self._covid)
            - all(len(self._high[x]) > 2 for x in self._high)
            - all(len(self._low[x]) > 2 for x in self._low)
            - all(len(self._open[x]) > 2 for x in self._open)
            - all(len(self._close[x]) > 2 for x in self._close)
            - len(matching_spikes(self._high[stock], self._covid[country], threshold)[0]) > 2

        >>> usa_and_snp = DataManager({'data/stock-snp500.csv', 'data/covid-usa.csv'}, datetime.date(2020, 6, 1), \
                            datetime.date(2021, 1, 10))
        >>> usa_and_snp.get_weekly_local_statistics('close', 'snp500', 'usa', 2000)
        0.20409776423112042
        """
        if stock_stream == 'high':
            spike_data = matching_spikes(self._high[stock], self._covid[country], stock, threshold)
        elif stock_stream == 'low':
            spike_data = matching_spikes(self._low[stock], self._covid[country], stock, threshold)
        elif stock_stream == 'open':
            spike_data = matching_spikes(self._open[stock], self._covid[country], stock, threshold)
        else:
            spike_data = matching_spikes(self._close[stock], self._covid[country], stock,   threshold)
        final_corr = return_correlation_coefficient(spike_data[0], spike_data[1])
        return final_corr


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


def spike_determiner(stock: list[float], covid: list[float], stocks: str, threshold: int) -> list[int]:
    """Checks to see what time periods count as spikes in both stock price and covid numbers
     and returns those indices with a threshold of 1 day.

    Preconditions:
        - len(stock) == len(covid)
        - stocks in {'tx60', snp500}
    >>> stock = [1, 75, 80, 100, 46]
    >>> covid = [2000, 1324, 1678, 1232, 1899]
    >>> spike_determiner(stock, covid, 1500)
    [0, 2]

    """
    spikes = []
    if stocks == 'tx60':
        stock_spike = 20.0
    else:
        stock_spike = 50.0
    for x in range(len(stock) - 1):
        if abs(stock[x + 1]) >= stock_spike and covid[x] >= threshold:
            spikes.append(x)
    return spikes


def matching_spikes(stock: list[float], covid: list[float], stocks: str, threshold: int) \
        -> list[list[int], list[int]]:
    """Matching the day of the first time covid broke the threshold with the first day of
    the first stock spike. Will return list with the covid spike indices lined up with the
    correlating stock spike indices.

    Preconditions:
        - len(stock) == len(covid)
        - all(x < len(covid) for x in spikes)
        - all(x < len(stock) - 1 for x in spikes)
        - stocks in {'tx60', snp500}

    >>> stock = [1, 75, 80, 100, 46]
    >>> covid = [2000, 1324, 1678, 1232, 1899]
    >>> matching_spikes(stock, covid, 1500)
    [[2000, 1678], [75, 100]]
    """
    final_data = [[], []]
    spikes = spike_determiner(stock, covid, stocks, threshold)
    for x in spikes:
        final_data[0].append(covid[x])
        final_data[1].append(stock[x + 1])
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


def return_correlation_coefficient(covid: list[float], stock: list[float]) -> any:
    """Returns correlation matrix from the data

    Preconditions
        - len(convert_data(covid, stock)) > 2
    >>> import math
    >>> c = return_correlation_coefficient([0.2 , 0.0, 0.6, 0.2], [0.3, 0.6, 0.0, 0.1])
    >>> math.isclose(-0.8510644963469901, c)
    True
    """
    data = convert_data(covid, stock)
    df = pd.DataFrame(data, columns=['covid', 'stocks'])
    correlation = df.corr()
    # FIXME: not rly a fix me but check if we want to go with this if statement
    #  to avoid callback errors
    if correlation.empty or correlation['covid']['stocks'] >= 1.0:
        return 0.0
    else:
        return correlation['covid']['stocks']
