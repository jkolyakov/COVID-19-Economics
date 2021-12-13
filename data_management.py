"""COVID-19 Economics - Data Management Backend

This module consists of a single class, DataManager, which acts as a backend to
the user interface.  This class manages the general state of the data that is
being analyzed and coordinates the actual data manipulation.

This file is Copyright (C) 2021, Theodore Preduta and Jacob Kolyakov.
"""
import datetime

from parse_data import parse_covid_data_file, parse_stock_data_file
from process_data import fill_covid_data, fill_stock_data, differentiate_stock_data, \
    calculate_correlation_coefficient, matching_spikes


class DataManager:
    """Manage the state of the data analysis.  This storing the data and dispatching the correct
    methods to process requests for specific analyses.

    Because the primary job of this class is to manage the state of the data, most of the actual
    calculations are done in a separate module.

    Representation Invariants:
        - len(self._stocks) == 4
        - all(s in self._stocks for s in {'open', 'close', 'high', 'low'})
        - self._start < self._end
        - self._duration > 0

    >>> dm = DataManager({'data/stock-snp500.csv', 'data/covid-usa.csv'}, \
                         datetime.date(2021, 1, 1), datetime.date(2021, 1, 10))
    """
    # Private Instance Attributes:
    #     - _covid: A mapping from a country code the the new covid cases reported at that day.
    #               The index in the list represents the number of days since _start.
    #     - _stocks: A mapping from a stock stream (open/high/low/close), to a mapping from the
    #                stock code to a list of the price change from yesterday.  By using a mapping
    #                instead of a dataclass we can achieve a more dynamic behaviour avoiding a
    #                large if statement block.
    #     - _start: The start date of the time period being analyzed.
    #     - _end: The end date of the time period being analyzed.  Note that this date is included
    #             in the time range.
    #     - _duration: The length (in days) of the period being analyzed.
    _covid: dict[str, list[int]]
    _stocks: dict[str, dict[str, list[float]]]
    _start: datetime.date
    _end: datetime.date
    _duration: int

    def __init__(self, sources: set[str], start: datetime.date, end: datetime.date) -> None:
        """Load the data from the files in sources, only from start to end inclusive.

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

                # Invariants
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

                # Invariants
                assert len(self._stocks['open'][name]) == self._duration
                assert len(self._stocks['high'][name]) == self._duration
                assert len(self._stocks['low'][name]) == self._duration
                assert len(self._stocks['close'][name]) == self._duration
            else:
                raise AssertionError('Invalid data type.')

    def get_global_statistics(self, stock_stream: str, days: int, stock: str,
                              country: str) -> list[float]:
        """Calculate the correlation coefficient of stock_stream for the combination of stock and
        country over with a shift from 0 to days inclusive.  The index of the returned list is
        equal to the shift applied for that correlation coefficient.

        Logic:
            1. ASSUME that the reaction time of the stock market is constant.
            2. Therefore, if we shift the stock data back, the correlation coefficient will spike
               to a statistically significant value at a single point.

        Preconditions:
            - stock_stream in {'high', 'low', 'open', 'close'}
            - days > 0
            - stock in self._stocks[stock_stream]
            - country in self._covid

        >>> # TODO maybe?
        """
        initial_corr = calculate_correlation_coefficient(self._covid[country],
                                                         self._stocks[stock_stream][stock])
        data_so_far = [initial_corr]

        for shift in range(1, days + 1):
            stock_data = self._stocks[stock_stream][stock][shift:]
            covid_data = self._covid[country][:-shift]
            corr = calculate_correlation_coefficient(covid_data, stock_data)
            data_so_far.append(corr)

        return data_so_far

    def get_local_statistics(self, stock_stream: str, stock: str, country: str,
                             max_gap: int) -> float:
        """Calculate the correlation correlation coefficient of stock_stream for the combination
        of stock and county assuming a reaction time of spikes at most max_gap days.

        Logic:
            1. ASSUME that IF the stock reacts, it will react within max_dap days.
            2. ASSUME that the stock market only makes big jumps because of covid.
            3. Therefore because of (1) IF the stock reacts there will be a matching spike within
               a max_gap interval.
            4. Therefore because of (2) IF there is a reaction in the stock market, there must
               have been a covid spike within a max_gap interval.
            5. Therefore IF (3) and (4), by matching the spikes up in a greedy way, the correlation
               coeficient, will be statistically signficant.

        Preconditions:
            - stock_stream in {'high', 'low', 'open', 'close'}
            - country in self._covid
            - stock in self._stocks[stock_stream]
            - max_gap >= 0

        >>> # TODO maybe?
        """
        if max_gap is None:
            max_gap = 0
        data = matching_spikes(self._stocks[stock_stream][stock],
                               self._covid[country], stock, country, max_gap)
        return calculate_correlation_coefficient(data[0], data[1])


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
