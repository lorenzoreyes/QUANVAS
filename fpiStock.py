import pandas as pd
import numpy as np
import yfinance as yahoo
import datetime as dt
import matplotlib.pyplot as plt
from pylab import mpl
mpl.rcParams['font.family'] = 'serif'
plt.style.use('fivethirtyeight')

stock = input('stock to backtest?\t\n')

data = yahoo.download(stock,period='3y')#,interval='60m')
df = data.pct_change()
#df = df[df<0].fillna(method='ffill')

fpi = df['Adj Close'] - (df['Adj Close'].rolling(20,min_periods=1).std() / df['Volume'].rolling(20,min_periods=1).std()) * df['Volume']

sigma1 = fpi.rolling(20,min_periods=1).std() * 1.64
sigma2 = fpi.rolling(20,min_periods=1).std() * 1.96
sigma3 = fpi.rolling(20,min_periods=1).std() * 2.56

watch = pd.DataFrame(index=fpi.index)
watch['serie'] = fpi#.rolling(20,min_periods=1).mean()
# generamos señales condicionales de 1, 2 y 3 std Indicio de crisis, Crisis y Megacrisis
watch['indicio'] = 0
watch['indicio'][:] = np.where(watch.serie > sigma1, 0.04, None)
watch['serio'] = 0
watch['serio'][:] = np.where(watch.serie > sigma2, 0.06, None)
watch['alarma'] = 0
watch['alarma'][:] = np.where(watch.serie > sigma3, 0.08, None)

indicio = watch[watch.indicio>=0.0].index.to_list()
serio = watch[watch.serio>=0].index.to_list()
alarma = watch[watch.alarma>=0].index.to_list()

plt.figure(figsize=(20,8))
plt.scatter(data.loc[indicio].index,data.loc[indicio]['Adj Close'],marker='v',c='yellow',s=200)
plt.scatter(data.loc[serio].index,data.loc[serio]['Adj Close'],marker='v',c='orange',s=600)
plt.scatter(data.loc[alarma].index,data.loc[alarma]['Adj Close'],marker='v',c='crimson',s=1200)

plt.plot(data['Adj Close'],alpha=0.8)