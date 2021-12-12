"""
TODO

This file acts as a state backend.
"""
import datetime

import pandas as pd

from parse_data import parse_covid_data_file, parse_stock_data_file
from process_data import fill_covid_data, fill_stock_data, differentiate_stock_data, \
    return_correlation_coefficient, matching_spikes


class DataManager:
    """Data manager class that will both store and handle processing data from the CSV files
    into a form that can be used by the Pandas library to calculate a correlation coefficient.
    TODO: Check if this is OK
    TODO: do doctests make any sense in this file?

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
            spike_data = matching_spikes(self._close[stock], self._covid[country], stock, threshold)
        final_corr = return_correlation_coefficient(spike_data[0], spike_data[1])
        return final_corr


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': [],  # TODO
        'allowed-io': [],  # TODO
        'max-line-length': 100,
        'disable': ['R1705', 'C0200']
    })

    import python_ta.contracts
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
