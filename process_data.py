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


def inflated_abs_average(data: list[Union[int, float]]) -> float:
    """Find the average of the magnitude of the lements of data, dropping all 0 values.

    We drop all 0 values under the assumption that they were added by fill_*_data at some point
    in the past (which is true with the dataset and time range).

    Preconditions:
        - data != []
        - any(x != 0 for x in data)

    >>> inflated_abs_average([0, 0, 0, 0, 0, 0, 1, -1])
    1.0
    >>> inflated_abs_average([0, 0, -10.0, 0])
    10.0
    """
    inflated_data = [abs(x) for x in data if x != 0]
    return sum(inflated_data) / len(inflated_data)


def find_matching_spikes(stock: list[float], covid: list[int], max_gap: int) \
        -> tuple[list[float], list[int]]:
    """Matching the day of the first time covid broke the threshold with the first day of
    the first stock spike. Will return list with the covid spike indices lined up with the
    correlating stock spike indices.

    Preconditions:
        - len(stock) == len(covid)
        - max_gap >= 0
        - stock != []
        - covid != []

    >>> stock = [1.0, 1.0, 0.0, 1.0, 0.0]
    >>> covid = [  1,   0,   1,   0,   0]
    >>> find_matching_spikes(stock, covid, 0)
    ([1.0, 1.0, 0.0, 1.0], [1, 0, 1, 0])
    >>> stock = [1.0, 1.0, 0.0, 1.0, 0.0]
    >>> covid = [  1,   0,   1,   0,   0]
    >>> find_matching_spikes(stock, covid, 2)
    ([1.0, 1.0, 1.0], [1, 1, 0])
    """
    stock_threshold = inflated_abs_average(stock)
    covid_threshold = inflated_abs_average(covid)

    stock_spikes_so_far = []
    covid_spikes_so_far = []

    stock_index = 0
    covid_index = 0
    while stock_index < len(stock) or covid_index < len(covid):
        while stock_index < len(stock) and abs(stock[stock_index]) < stock_threshold:
            stock_index += 1

        while covid_index < len(covid) and abs(covid[covid_index]) < covid_threshold:
            covid_index += 1

        if stock_index >= len(stock) and covid_index >= len(covid):
            break
        elif stock_index >= len(stock):
            stock_spikes_so_far.append(0.0)
            covid_spikes_so_far.append(covid[covid_index])
            covid_index += 1
        elif covid_index >= len(covid):
            stock_spikes_so_far.append(stock[stock_index])
            covid_spikes_so_far.append(0)
            stock_index += 1
        elif abs(stock_index - covid_index) <= max_gap:
            stock_spikes_so_far.append(stock[stock_index])
            covid_spikes_so_far.append(covid[covid_index])
            covid_index += 1
            stock_index += 1
        elif covid_index < stock_index:
            stock_spikes_so_far.append(0.0)
            covid_spikes_so_far.append(covid[covid_index])
            covid_index += 1
        else:
            stock_spikes_so_far.append(stock[stock_index])
            covid_spikes_so_far.append(0)
            stock_index += 1

    return (stock_spikes_so_far, covid_spikes_so_far)


def convert_to_lengthwise(covid: list[float], stock: list[float]) -> list[tuple]:
    """Converts spike data into form that will be accepted by the Panda's library DataFrame class.

    Preconditions:
        - len(covid) == len(stock)

    >>> convert_to_lengthwise([0.2 , 0.0, 0.6, 0.2], [0.3, 0.6, 0.0, 0.1])
    [(0.2, 0.3), (0.0, 0.6), (0.6, 0.0), (0.2, 0.1)]
    """
    final_data = []
    for i in range(len(covid)):
        final_data.append((covid[i], stock[i]))
    return final_data


def find_correlation_coefficient(covid: list[float], stock: list[float]) -> float:
    """Returns correlation coefficient of covid against stock, assuming that that equal indices
    imply equal dates.

    Preconditions
        - len(covid) == len(stock)
        - len(convert_data(covid, stock)) > 2

    >>> import math
    >>> c = find_correlation_coefficient([0.2 , 0.0, 0.6, 0.2], [0.3, 0.6, 0.0, 0.1])
    >>> math.isclose(-0.8510644963469901, c)
    True
    """
    data = convert_to_lengthwise(covid, stock)
    df = pd.DataFrame(data, columns=['covid', 'stocks'])
    correlation = df.corr()

    # If there is not enough data to calculate a correlation coefficient, for our purposes it
    # suffices that we can say there is 0 correlation.  This avoids complexity in the caller.
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
