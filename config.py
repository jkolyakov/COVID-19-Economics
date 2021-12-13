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

# TODO description
STYLE_URL = 'https://gist.githubusercontent.com/6167656e74323431/b218f77e072c4'\
            '0746de03d6d7f74ce1f/raw/0570945d49e80be0d889d6f2774aad1d4954a77c/'\
            'style.css'
# If this isn't reason enough for python-ta to allow longer strings, i don't
# know what is. :-)

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
