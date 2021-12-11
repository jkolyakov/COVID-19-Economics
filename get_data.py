"""
File for getting the data from external sources. Currently only for the snp500 stock values
"""

import yfinance as yf
import pandas as pd


def get_snp500_data() -> None:
    """This function will download the historical data for the snp500 from yfinance
    and format it in a csv file"""
    data = yf.download('^GSPC', start='2018-01-01', end='2021-11-20')
    print(data)
    data.to_csv("snp500-data.csv")
    f = pd.read_csv("snp500-data.csv")
    keep_col = ['Date', 'Open', 'High', 'Low', 'Close']
    new_f = f[keep_col]
    new_f.to_csv("snp500-data1.csv", index=False)
