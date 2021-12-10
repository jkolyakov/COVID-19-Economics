import yfinance as yf  # TODO: Not in usable state (should not run immediately, create functions)
import pandas as pd

data = yf.download('^GSPC', start='2018-01-01', end='2021-11-20')
print(data)
data.to_csv("snp500-data.csv")
f = pd.read_csv("snp500-data.csv")
keep_col = ['Date', 'Open', 'High', 'Low', 'Close']
new_f = f[keep_col]
new_f.to_csv("snp500-data1.csv", index=False)
