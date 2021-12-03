import yfinance as yahoo
import pandas as pd
import matplotlib.pyplot as plt
from pylab import mpl
mpl.rcParams['font.family'] = 'serif'
plt.style.use('fivethirtyeight')


time, duration = "252d", "60m"

stocks = ['AAPL.BA', 'BBD.BA', 'MELI.BA', 'KO.BA', 'INTC.BA', 'VALE.BA',
       'TSLA.BA', 'WFC.BA', 'XOM.BA', 'AMZN.BA', 'BABA.BA', 'T.BA', 'MSFT.BA',
       'GE.BA', 'WMT.BA', 'HMY.BA', 'PFE.BA', 'ERJ.BA', 'AUY.BA', 'X.BA']

#cedears = yahoo.download(stocks, period=time, interval=duration)['Adj Close'].fillna(method='ffill')
cedears = yahoo.download(stocks, period=time)['Adj Close'].fillna(method='ffill')
ratios = [10,144,1,9,1,1,1,1,5,5,60,10,2,3,15,2,5,6,3,5]

cedears = cedears * ratios  # get stocks prices according to what you have to paid

topba = [s.replace('.BA', 'BA') for s in stocks]

cedears.columns = topba

forex = [i.replace('.BA','') for i in stocks]

#df = yahoo.download(forex,period=time, interval=duration)['Adj Close'].fillna(method='ffill')
df = yahoo.download(forex,period=time)['Adj Close'].fillna(method='ffill')
mervalba = ['ARS=X', 'BMA', 'BMA.BA', 'CEPU', 'CEPU.BA', 'CRES.BA', 'CRESY', 'EDN', 'EDN.BA',
            'GGAL', 'GGAL.BA', 'IRS', 'IRSA.BA', 'LOMA', 'LOMA.BA', 'PAM', 'PAMP.BA',
            'SUPV', 'SUPV.BA', 'TECO2.BA', 'TEO', 'TGS', 'TGSU2.BA', 'YPF',
            'YPFD.BA']

#merval = yahoo.download(tickers=mervalba, period=time, interval=duration)['Adj Close'].fillna(method='ffill')
merval = yahoo.download(tickers=mervalba, period=time)['Adj Close'].fillna(method='ffill')
top = list(merval.columns)
topmerval = [t.replace('.BA', 'BA') for t in top]

merval.columns = topmerval

cable = pd.DataFrame(data=None)

cable['BMA'] = (merval.BMABA / merval.BMA) * 10
cable['CEPU'] = (merval.CEPUBA / merval.CEPU) * 10
cable['CRES'] = (merval.CRESBA / merval.CRESY) * 10
cable['EDN'] = (merval.EDNBA / merval.EDN) * 20
cable['GGAL'] = (merval.GGALBA / merval.GGAL) * 10
cable['IRSA'] = (merval.IRSABA / merval.IRS) * 10
cable['LOMA'] = (merval.LOMABA / merval.LOMA) * 5
cable['PAMP'] = (merval.PAMPBA / merval.PAM) * 25
cable['SUPV'] = (merval.SUPVBA / merval.SUPV) * 5
cable['TECO2'] = (merval.TECO2BA / merval.TEO) * 5
cable['TGSU2'] = (merval.TGSU2BA / merval.TGS) * 5
cable['YPF'] = (merval.YPFDBA / merval.YPF)

mediacable = pd.DataFrame(index=cable.index)
mediacable['CableAdrs'] = cable.T.median()

df = df.tail(len(cedears))

tc = cedears.div(df.values)
tc.columns = topba

mediaced = pd.DataFrame(index=tc.index)
mediaced['CableCedears'] = tc.T.median()

dolar = pd.DataFrame(index=merval.index)
dolar['solidario+30+35'] = merval.iloc[:, 0] * 1.30 * 1.35


mep = pd.DataFrame(mediaced.values,columns=['Cedears Rate'],index=mediaced.index)
mep['ADRs Rate'] = mediacable.tail(len(mep)).values
mep['Dollar+Taxes'] = dolar.tail(len(mep)).values

retorno = mep.copy()
mep.to_csv('Exchanges.csv')
mep = mep.rename(columns={'Cedears Rate':f'Cedears Rate $ {round(mep["Cedears Rate"].values[-1],2)}'})
mep = mep.rename(columns={'ADRs Rate':f'ADRs Rate      $ {round(mep["ADRs Rate"].values[-1],2)}'})
mep = mep.rename(columns={'Dollar+Taxes':f'Dollar+Taxes  $ {round(mep["Dollar+Taxes"].values[-1],2)}'})

retorno= retorno.rename(columns={'Cedears Rate':f'Cedears Rate % {round(retorno["Cedears Rate"].pct_change().sum()*100.0,2)}'})
retorno = retorno.rename(columns={'ADRs Rate':f'ADRs Rate      % {round(retorno["ADRs Rate"].pct_change().sum()*100.0,2)}'})
retorno = retorno.rename(columns={'Dollar+Taxes':f'Dollar+Taxes   % {round(retorno["Dollar+Taxes"].pct_change().sum()*100.0,2)}'})


fig = plt.figure(figsize=(16,8))
ax1 = fig.add_subplot(111)
mep.fillna(method='ffill').plot(ax=ax1,lw=5.,legend=True)
ax1.set_title('Exchange Rates Argentina',fontsize=60,fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=2)
ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=30)
plt.xticks(size=20)
plt.yticks(size=20)
plt.savefig('Exchanges.png',bbox_inches='tight')

fig = plt.figure(figsize=(16,8))
ax1 = fig.add_subplot(111)
retorno.fillna(method='ffill').pct_change().cumsum().plot(ax=ax1,lw=5.,legend=True)
ax1.set_title('Exchange Rates Return Argentina',fontsize=60,fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=2)
ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=30)
plt.xticks(size=20)
plt.yticks(size=20)
plt.savefig('ExchangesReturn.png',bbox_inches='tight')
