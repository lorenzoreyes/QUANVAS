import scrap
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
from pylab import mpl
mpl.rcParams['font.family'] = 'serif'
plt.style.use('fivethirtyeight')

binance = scrap.binance()
df = binance[0]

columnas = []
for i in range(len(df.columns)):
    columnas.append(str(round(df.iloc[:,i].pct_change().sum(),2)) + '% ' + str(df.columns[i]))

df.columns = columnas
df = df.reindex(sorted(df.columns,reverse=True), axis=1)

fig = plt.figure(figsize=(30,15))
ax1 = fig.add_subplot(111)
df.pct_change().cumsum().plot(ax=ax1, lw=5)
ax1.set_title('Binance TOP30', fontsize=50, fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=2)
ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=30)
plt.xticks(size=40)
plt.yticks(size=40)
plt.savefig('binance.png',bbox_inches='tight')