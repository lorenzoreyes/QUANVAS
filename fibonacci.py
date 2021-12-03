import yfinance as yahoo
import pandas as pd
import datetime as dt
import numpy as np
import scipy.optimize as sco
from scipy import stats
import matplotlib.pyplot as plt
from pylab import mpl
mpl.rcParams['font.family'] = 'serif'
plt.style.use('fivethirtyeight')

# Fibonacci Levels considering original trend as upward move
stock = input('Calculate Fibonacci of this stock\t\t\n')
data = yahoo.download(stock,period="1y")["Adj Close"]
price_max,price_min = data.max(), data.min()
diff = price_max - price_min
level1 = price_max - 0.236 * diff
level2 = price_max - 0.382 * diff
level3 = price_max - 0.618 * diff

fig, ax = plt.subplots()
ax.plot(data, color='black')
ax.axhspan(level1, price_min, alpha=0.4, color='lightsalmon')
ax.axhspan(level2, level1, alpha=0.5, color='palegoldenrod')
ax.axhspan(level3, level2, alpha=0.5, color='palegreen')
ax.axhspan(price_max, level3, alpha=0.5, color='powderblue')

plt.ylabel("Price")
plt.xlabel("Date")
plt.legend(loc=2)
plt.show()