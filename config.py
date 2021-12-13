"""COVID-19 Economics - Project Configuration

This module consists of constants used to define the scope of the analysis of
this program.

This file is Copyright (C) 2021, Theodore Preduta and Jacob Kolyakov.
"""
import datetime

# The set of data files that will be analyzed.
DATA_FILES = {
    'data/covid-can.csv',
    'data/covid-chn.csv',
    'data/covid-usa.csv',
    'data/stock-snp500.csv',
    'data/stock-tx60.csv'
}

# The time range of the analysis.
START_DATE = datetime.date(2020, 1, 1)
END_DATE = datetime.date(2021, 11, 1)

# Sets of only the country codes or the stock codes.
ALL_COUNTRIES = {
    'can',
    'chn',
    'usa'
}
ALL_STOCKS = {
    'snp500',
    'tx60'
}

# Mapping of the codes to longer english names used for display purposes.
LONG_NAMES = {
    # Countries
    'can': 'Canada',
    'chn': 'China',
    'usa': 'United States of America',

    # Stocks
    'snp500': 'SNP500',
    'tx60': 'TX60'
}

if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['datetime'],
        'allowed-io': [],
        'max-line-length': 100,
        'disable': ['R1705', 'C0200']
    })

    import python_ta.contracts
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
