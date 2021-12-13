"""COVID-19 Economics - Data Management Backend

This module consists of a single class, DataManager, which acts as a backend to
the user interface.  This class manages the general state of the data that is
being analyzed and coordinates the actual data manipulation.

This file is Copyright (C) 2021, Theodore Preduta and Jacob Kolyakov.
"""
import datetime

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
    _stocks: dict[str, dict[str, list[float]]]
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
        self._stocks = {
            'open': {},
            'high': {},
            'low': {},
            'close': {}
        }
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
                                                     end)

                data = [differentiate_stock_data(x) for x in data]
                dates.pop(0)  # the above implicitly chops off the first element

                data = [fill_stock_data(dates, x, start, end) for x in data]

                self._stocks['open'][name] = data[0]
                self._stocks['high'][name] = data[1]
                self._stocks['low'][name] = data[2]
                self._stocks['close'][name] = data[3]

                assert len(self._stocks['open'][name]) == self._duration
                assert len(self._stocks['high'][name]) == self._duration
                assert len(self._stocks['low'][name]) == self._duration
                assert len(self._stocks['close'][name]) == self._duration
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

    def get_global_statistics(self, stock_stream: str, days: int, stock: str,
                              country: str) -> list[float]:
        """TODO: write this descirption again

        Logic:
            1. ASSUME that the reaction time of the stock market is constant.
            2. Therefore, if we shift the stock data back, the correlation coefficient will spike
               to a statistically significant value at a single point.

        Preconditions:
            - stock_stream in {'high', 'low', 'open', 'close'}
            - days > 0
            - stock in self._open
            - country in self._covid
            - all(len(self._covid[x]) > 2 for x in self._covid)
            - all(len(self._high[x]) > 2 for x in self._high)
            - all(len(self._low[x]) > 2 for x in self._low)
            - all(len(self._open[x]) > 2 for x in self._open)
            - all(len(self._close[x]) > 2 for x in self._close) # TODO fix these

        >>> # TODO
        # TODO: check if lack of data causes error
        """
        initial_corr = return_correlation_coefficient(self._covid[country],
                                                      self._stocks[stock_stream][stock])
        data_so_far = [initial_corr]

        for shift in range(1, days):
            stock_data = self._stocks[stock_stream][stock][shift:]
            covid_data = self._covid[country][:-shift]
            corr = return_correlation_coefficient(covid_data, stock_data)
            data_so_far.append(corr)

        return data_so_far

    def get_local_statistics(self, stock_stream: str, stock: str, country: str,
                             max_gap: int) -> float:
        """TODO write this description

        Logic:
            1. ASSUME that IF the stock reacts, it will react within max_dap days.
            2. ASSUME that IF the stock reacts, it will react for each spike in the covid data.
            3. ASSUME that IF for every stock spike, there should be COVID spike.
            4. Therefore if this is true, by matching the spikes up in a greedy way, the correlation
               coeficient, will be statistically signficant.

        TODO reword 2 and 3

        Preconditions:
            - stock_stream in {'high', 'low', 'open', 'close'}
            - stock in self._open
            - country in self._covid
            - all(len(self._covid[x]) > 2 for x in self._covid) # TODO this needs to be redone
            - all(len(self._high[x]) > 2 for x in self._high)   #  after the change to the new
            - all(len(self._low[x]) > 2 for x in self._low)     #  format
            - all(len(self._open[x]) > 2 for x in self._open)
            - all(len(self._close[x]) > 2 for x in self._close)
            - len(matching_spikes(self._high[stock], self._covid[country], threshold)[0]) > 2

        >>> # TODO
        """
        if max_gap is None:
            max_gap = 0
        data = matching_spikes(self._stocks[stock_stream][stock],
                               self._covid[country], stock, country, max_gap)
        return return_correlation_coefficient(data[0], data[1])


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['datetime', 'pandas', 'parse_data', 'process_data'],
        'allowed-io': [],
        'max-line-length': 100,
        'disable': ['R1705', 'C0200']
    })

    import python_ta.contracts
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
