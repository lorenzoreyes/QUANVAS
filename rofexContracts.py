import pyRofex
import urllib.request
import pandas as pd
import datetime as dt 
import yfinance as yahoo
import matplotlib.pyplot as plt 
from pylab import mpl
mpl.rcParams['font.family'] = 'serif'
plt.style.use('fivethirtyeight')

pyRofex.initialize(user="MD_REYES",
                   password="Lorenzo6+",
                   account="88406W",
                   environment=pyRofex.Environment.LIVE)

futuros = [i['instrumentId']['symbol'] for i in pyRofex.get_all_instruments()['instruments']]

futuros = pd.DataFrame(futuros,columns=['Contratos'],index=range(len(futuros)))

products = []
for i in range(len(futuros)):
    if f'{futuros.Contratos.values[i]}'[0:3] not in products:
        products.append(f'{futuros.Contratos.values[i]}'[0:3])
    else:
        pass