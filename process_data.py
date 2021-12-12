"""
This file is where the acutal data processing happens
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
    >>> spike_determiner(stock, covid, 1500)  # FIXME this does not work
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
    >>> matching_spikes(stock, covid, 1500) # FIXME this does not work
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
