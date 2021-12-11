"""
File for getting/formatting the data for external sources. Currently for all stock data
"""

import yfinance as yf
import pandas as pd


def get_snp500_data() -> None:
    """This function will download the historical data for the snp500 from yfinance
    and format it in a csv file"""
    data = yf.download('^GSPC', start='2018-01-01', end='2021-11-20')
    print(data)
    data.to_csv("data/snp500-data.csv")
    f = pd.read_csv("data/snp500-data.csv")
    keep_col = ['Date', 'Open', 'High', 'Low', 'Close']
    new_f = f[keep_col]
    new_f.to_csv("data/snp500-data.csv", index=False)


def fix_tx60() -> None:
    """This function will fix the formatting of the tx60 data into a csv file that will be
    correctly parsed"""
    f = pd.read_csv("data/stock-tx60.csv")
    keep_col = ['Date', 'Open', 'High', 'Low', 'Close']
    new_f = f[keep_col]
    new_f = new_f.apply(lambda x: x.str.replace(',', ''))
    new_f['Date'] = pd.to_datetime(new_f['Date'], format='%b %d %Y')
    final_f = new_f
    final_f.to_csv("data/stock-tx60.csv", index=False)
