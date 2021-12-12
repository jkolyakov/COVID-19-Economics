"""
Useful constants.
"""

import datetime

# TODO description
DATA_FILES = {
    'data/covid-can.csv',
    'data/covid-chn.csv',
    'data/covid-usa.csv',
    'data/stock-snp500.csv',
    'data/stock-tx60.csv'
}

# TODO description
START_DATE = datetime.date(2020, 1, 1)
END_DATE = datetime.date(2021, 1, 1)

# TODO description
ALL_COUNTRIES = {
    'can',
    'chn',
    'usa'
}
ALL_STOCKS = {
    'snp500',
    'tx60'
}

# TODO description
LONG_NAMES = {
    # Countries
    'can': 'Canada',
    'chn': 'China',
    'usa': 'United States of America',

    # Stocks
    'snp500': 'SNP500',
    'tx60': 'TX60'
}
