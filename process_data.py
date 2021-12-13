"""COVID-19 Economics - Data Processing

This module consists of helper functions that perform the data manipulations
and call into the pandas module.

This file is Copyright (C) 2021, Theodore Preduta and Jacob Kolyakov.
"""
import datetime
from typing import Union

import pandas as pd


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

    >>> fill_covid_data([datetime.date(2021, 1, 2), datetime.date(2021, 1, 4)], \
                        [1, 2], datetime.date(2021, 1, 1), datetime.date(2021, 1, 4))
    [0, 1, 0, 2]
    """
    filled_data = [0] * ((end - start).days + 1)
    fill_data(dates, data, filled_data, start)
    return filled_data


def fill_data(dates: list[datetime.date], data: list[Union[int, float]],
              base: list[Union[int, float]], start: datetime.date) -> None:
    """Backend function for fill_covid_data and fill_stock_data.  Actually performs the copy in a
    type agnostic way.

    Preconditions:
        - len(data) == len(dates)
        - TODO preconditions on each date in dates

    >>> dates = [datetime.date(2021, 1, 2), datetime.date(2021, 1, 4), datetime.date(2021, 1, 10)]
    >>> data = [1, 2, 3]
    >>> base = [0] * 10
    >>> start = datetime.date(2021, 1, 1)
    >>> fill_data(dates, data, base, start)
    >>> base
    [0, 1, 0, 2, 0, 0, 0, 0, 0, 3]
    """
    for i in range(len(dates)):
        actual_index = (dates[i] - start).days
        base[actual_index] = data[i]


def is_stock_spike(stock: list[float], stocks: str, stock_index: int) -> bool:
    """Checks to see what time periods count as spikes in both stock price and covid numbers
     and returns those indices with a threshold of 1 day.

    Preconditions:
        - len(stock) == len(covid)
        - stocks in {'tx60', snp500}
        - index < len(stock) and index < len(covid)
    >>> stock = [1, 75, 80, 100, 46]
    >>> covid = [2000, 1324, 1678, 1232, 1899]
    # >>> is_spike(stock, covid)  # FIXME this does not work
    [0, 2]

    """
    if stocks == 'tx60':
        stock_spike = 20.0
    else:
        stock_spike = 50.0
    if abs(stock[stock_index]) >= stock_spike:
        return True
    else:
        return False


def is_covid_spike(covid: list[float], country: str, covid_index: int) -> bool:
    """Checks to see what time periods count as spikes in both stock price and covid numbers
        and returns those indices with a threshold of 1 day.

       Preconditions:
           - len(stock) == len(covid)
           - stocks in {'tx60', snp500}
           - index < len(stock) and index < len(covid)
       >>> stock = [1, 75, 80, 100, 46]
       >>> covid = [2000, 1324, 1678, 1232, 1899]
       # >>> is_spike(stock, covid)  # FIXME this does not work
       [0, 2]

       """
    if country == 'can':
        covid_spike = 1610
    elif country == 'usa':
        covid_spike = 55384
    else:
        covid_spike = 235
    if covid[covid_index] >= covid_spike:
        return True
    else:
        return False


def append_matching_spikes(stock: list[float], stocks: str, numbers: list[int],
                           stock_index_so_far: set, final_data: list[list]) -> bool:
    """A helper function for matching_spikes that checks for matching stock spike values
    within the allowed gap and returns whether one was found/added

    >>> # TODO
    """
    for y in range(numbers[0], numbers[0] + numbers[1] + 1):
        if y < len(stock) and is_stock_spike(stock, stocks, y) and y not in stock_index_so_far:
            final_data[1].append(stock[y])
            stock_index_so_far.add(y)
            return True
    return False


def matching_spikes(stock: list[float], covid: list[float], stocks: str, country: str,
                    max_gap: int) -> list[list[int], list[int]]:
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
    >>> matching_spikes(stock, covid, 1500) # FIXME this does not work
    [[2000, 1678], [75, 100]]
    """
    final_data = [[], []]

    stock_index_so_far = set()

    for x in range(len(covid)):
        if is_covid_spike(covid, country, x):
            final_data[0].append(covid[x])
            if_add = append_matching_spikes(stock, stocks,
                                            [x, max_gap], stock_index_so_far, final_data)
            if not if_add:
                final_data[1].append(0.0)
    for z in range(len(stock)):
        if is_stock_spike(stock, stocks, z) and z not in stock_index_so_far:
            final_data[0].append(0.0)
            final_data[1].append(stock[z])
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


def calculate_correlation_coefficient(covid: list[float], stock: list[float]) -> any:
    """Returns correlation matrix from the data

    Preconditions
        - len(convert_data(covid, stock)) > 2
    >>> import math
    >>> c = calculate_correlation_coefficient([0.2 , 0.0, 0.6, 0.2], [0.3, 0.6, 0.0, 0.1])
    >>> math.isclose(-0.8510644963469901, c)
    True

    # TODO rename this function
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


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['datetime', 'pandas'],
        'allowed-io': [],
        'max-line-length': 100,
        'disable': ['R1705', 'C0200']
    })

    import python_ta.contracts
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
