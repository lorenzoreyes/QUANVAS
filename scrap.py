import yfinance as yahoo 
import pandas as pd, numpy as np
import ssl
import urllib.request

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context
    #from pytickersymbols import PyTickerSymbols #https://pypi.org/project/pytickersymbols/


# functions to get info about each market and their current stock tickets
# markets to operate: USA (Nasdaq & SP500), England, China, Japan, Canada, Brazil, Australia
# the handlers will result with a list of metrics that will be use by main script
# to build respective portfolio

def GSPC():
    USA = pd.read_html("https://topforeignstocks.com/indices/components-of-the-sp-500-index/")[0]
    USA = list(USA.Ticker.values)
    freeRisk = '^GSPC'
    df = yahoo.download(USA,period="1y")["Adj Close"].fillna(method="ffill")
    pct = df.pct_change()#.dropna()
    mean = pd.DataFrame(pct.mean(),columns=['Mean'],index=pct.columns)
    riskpct = mean.mean()
    mean_rf = mean - riskpct.mean()
    std = pd.DataFrame(pct.std(),columns=['Std'],index=pct.columns)
    sharpe_ratio = pd.DataFrame(mean_rf['Mean']/(std['Std']), columns=['SharpeRatio'],index=pct.columns)
    orderedsharpe = sharpe_ratio.sort_values('SharpeRatio', axis=0, ascending=False)
    lista = list(orderedsharpe.head(50).index.values)
    df = yahoo.download(lista,period="1y",interval="60m")["Adj Close"].fillna(method="ffill")
    riskfree = yahoo.download(freeRisk, period="1y",interval="60m")['Adj Close'].fillna(method='ffill')
    pct = df.pct_change().dropna() #(how='all')
    riskpct = riskfree.pct_change().dropna()
    mean = pd.DataFrame(pct.mean(),columns=['Mean'],index=pct.columns)
    mean_rf = mean - riskpct.mean()
    std = pd.DataFrame(pct.std(),columns=['Std'],index=pct.columns)
    numerator = pct.sub(riskpct,axis=0)
    downside_risk = ((numerator[numerator<0].fillna(0))**2).mean()
    noa = len(df.columns)
    weigths = np.random.random(noa)
    weigths /= np.sum(weigths)
    observations = len(df.index)
    mean_returns = df.pct_change().mean()
    cov = df.pct_change().cov()
    alpha = 0.1
    rf = riskpct.mean()
    num_portfolios = 1000
    Upbound = 0.075
    result = [df,riskfree,pct,riskpct,mean,mean_rf,std,numerator,downside_risk,noa,weigths\
        ,observations,mean_returns,cov,alpha,rf,num_portfolios,Upbound]
    return result
    

def Cedears():
    comafi = pd.read_html('https://www.comafi.com.ar/2254-CEDEAR-SHARES.note.aspx')[0]
    # sorteamos por orden alfabético
    comafi = comafi.sort_values('Símbolo BYMA',axis=0,ascending=True)
    comafi.index = range(len(comafi)) # update index order values
    cells = list(comafi['Símbolo BYMA'].values)
    # cells.index('AAPL') way to get index number where ticker is located
    cedears = [c + '.BA' for c in cells]
    volume = yahoo.download(cedears,period="80d")['Volume'].fillna(method='ffill')
    votal = pd.DataFrame(index=volume.index)
    votal['totav'] = volume.T.sum()
    percentage = volume.div(votal['totav'], axis=0)
    ordered = pd.DataFrame(percentage.sum().T,columns=['percentage'],index=percentage.columns)
    ordered = ordered / ordered.sum() # ensure you round to 100%
    orderedalph = ordered.sort_values('percentage',axis=0,ascending=False)    
    liquid = orderedalph.cumsum()    
    listado = list(liquid.head(50).index.values)
    listado = [i.replace('.BA','') for i in listado]
    lista = []
    for i in range(len(listado)):
        lista.append(comafi['Ticker en Mercado de Origen'][cells.index(f'{listado[i]}')]) 
    freeRisk = '^GSPC'
    df = yahoo.download(lista,period="1y")["Adj Close"].fillna(method="ffill")
    pct = df.pct_change()#.dropna()
    mean = pd.DataFrame(pct.mean(),columns=['Mean'],index=pct.columns)
    riskpct = mean.mean()
    mean_rf = mean - riskpct.mean()
    std = pd.DataFrame(pct.std(),columns=['Std'],index=pct.columns)
    sharpe_ratio = pd.DataFrame(mean_rf['Mean']/(std['Std']), columns=['SharpeRatio'],index=pct.columns)
    orderedsharpe = sharpe_ratio.sort_values('SharpeRatio', axis=0, ascending=False)
    lista = list(orderedsharpe.head(50).index.values)
    df = yahoo.download(lista,period="1y",interval="60m")["Adj Close"].fillna(method="ffill")
    riskfree = yahoo.download(freeRisk, period="1y",interval="60m")['Adj Close'].fillna(method='ffill')
    pct = df.pct_change().dropna() #(how='all')
    riskpct = riskfree.pct_change().dropna()
    mean = pd.DataFrame(pct.mean(),columns=['Mean'],index=pct.columns)
    mean_rf = mean - riskpct.mean()
    std = pd.DataFrame(pct.std(),columns=['Std'],index=pct.columns)
    numerator = pct.sub(riskpct,axis=0)
    downside_risk = ((numerator[numerator<0].fillna(0))**2).mean()
    noa = len(df.columns)
    weigths = np.random.random(noa)
    weigths /= np.sum(weigths)
    observations = len(df.index)
    mean_returns = df.pct_change().mean()
    cov = df.pct_change().cov()
    alpha = 0.1
    rf = riskpct.mean()
    num_portfolios = 1000
    Upbound = 0.075
    result = [df,riskfree,pct,riskpct,mean,mean_rf,std,numerator,downside_risk,noa,weigths\
        ,observations,mean_returns,cov,alpha,rf,num_portfolios,Upbound]
    return result

def NIKKEI():
    nikkei = pd.read_html("https://topforeignstocks.com/indices/the-components-of-the-nikkei-225-index/")[0]
    nikkei['tickets'] = [t + '.T' for t in nikkei.Code.astype(str)]
    nikkei = list(nikkei.tickets.values)
    freeRisk = '^N225'
    df = yahoo.download(nikkei,period="1y")["Adj Close"].fillna(method="ffill")
    pct = df.pct_change()#.dropna()
    mean = pd.DataFrame(pct.mean(),columns=['Mean'],index=pct.columns)
    riskpct = mean.mean()
    mean_rf = mean - riskpct.mean()
    std = pd.DataFrame(pct.std(),columns=['Std'],index=pct.columns)
    sharpe_ratio = pd.DataFrame(mean_rf['Mean']/(std['Std']), columns=['SharpeRatio'],index=pct.columns)
    orderedsharpe = sharpe_ratio.sort_values('SharpeRatio', axis=0, ascending=False)
    lista = list(orderedsharpe.head(50).index.values)
    df = yahoo.download(lista,period="1y",interval="60m")["Adj Close"].fillna(method="ffill")
    riskfree = yahoo.download(freeRisk, period="1y",interval="60m")['Adj Close'].fillna(method='ffill')
    pct = df.pct_change().dropna() #(how='all')
    riskpct = riskfree.pct_change().dropna()
    mean = pd.DataFrame(pct.mean(),columns=['Mean'],index=pct.columns)
    mean_rf = mean - riskpct.mean()
    std = pd.DataFrame(pct.std(),columns=['Std'],index=pct.columns)
    numerator = pct.sub(riskpct,axis=0)
    downside_risk = ((numerator[numerator<0].fillna(0))**2).mean()
    noa = len(df.columns)
    weigths = np.random.random(noa)
    weigths /= np.sum(weigths)
    observations = len(df.index)
    mean_returns = df.pct_change().mean()
    cov = df.pct_change().cov()
    alpha = 0.1
    rf = riskpct.mean()
    num_portfolios = 1000
    Upbound = 0.075
    result = [df,riskfree,pct,riskpct,mean,mean_rf,std,numerator,downside_risk,noa,weigths\
        ,observations,mean_returns,cov,alpha,rf,num_portfolios,Upbound]
    return result

def Shanghai():
    china = pd.read_html('https://tradingeconomics.com/china/stock-market')[1]
    shanghai = [i + '.SS' for i in list(china['Unnamed: 0'].astype(str))]
    freeRisk = "000001.SS"
    df = yahoo.download(shanghai,period="1y")["Adj Close"].fillna(method="ffill")
    pct = df.pct_change()#.dropna()
    mean = pd.DataFrame(pct.mean(),columns=['Mean'],index=pct.columns)
    riskpct = mean.mean()
    mean_rf = mean - riskpct.mean()
    std = pd.DataFrame(pct.std(),columns=['Std'],index=pct.columns)
    sharpe_ratio = pd.DataFrame(mean_rf['Mean']/(std['Std']), columns=['SharpeRatio'],index=pct.columns)
    orderedsharpe = sharpe_ratio.sort_values('SharpeRatio', axis=0, ascending=False)
    lista = list(orderedsharpe.head(50).index.values)
    df = yahoo.download(lista,period="1y",interval="60m")["Adj Close"].fillna(method="ffill")
    riskfree = yahoo.download(freeRisk, period="1y",interval="60m")['Adj Close'].fillna(method='ffill')
    pct = df.pct_change().dropna() #(how='all')
    riskpct = riskfree.pct_change().dropna()
    mean = pd.DataFrame(pct.mean(),columns=['Mean'],index=pct.columns)
    mean_rf = mean - riskpct.mean()
    std = pd.DataFrame(pct.std(),columns=['Std'],index=pct.columns)
    numerator = pct.sub(riskpct,axis=0)
    downside_risk = ((numerator[numerator<0].fillna(0))**2).mean()
    noa = len(df.columns)
    weigths = np.random.random(noa)
    weigths /= np.sum(weigths)
    observations = len(df.index)
    mean_returns = df.pct_change().mean()
    cov = df.pct_change().cov()
    alpha = 0.1
    rf = riskpct.mean()
    num_portfolios = 1000
    Upbound = 0.075
    result = [df,riskfree,pct,riskpct,mean,mean_rf,std,numerator,downside_risk,noa,weigths\
        ,observations,mean_returns,cov,alpha,rf,num_portfolios,Upbound]
    return result

def BOVESPA():
    bovespa = pd.read_html("https://topforeignstocks.com/indices/components-of-the-bovespa-index/")[0]
    bovespa = list(bovespa.Ticker.values)
    freeRisk = '^BVSP'
    df = yahoo.download(bovespa,period="1y")["Adj Close"].fillna(method="ffill")
    pct = df.pct_change()#.dropna()
    mean = pd.DataFrame(pct.mean(),columns=['Mean'],index=pct.columns)
    riskpct = mean.mean()
    mean_rf = mean - riskpct.mean()
    std = pd.DataFrame(pct.std(),columns=['Std'],index=pct.columns)
    sharpe_ratio = pd.DataFrame(mean_rf['Mean']/(std['Std']), columns=['SharpeRatio'],index=pct.columns)
    orderedsharpe = sharpe_ratio.sort_values('SharpeRatio', axis=0, ascending=False)
    lista = list(orderedsharpe.head(50).index.values)
    df = yahoo.download(lista,period="1y",interval="60m")["Adj Close"].fillna(method="ffill")
    riskfree = yahoo.download(freeRisk, period="1y",interval="60m")['Adj Close'].fillna(method='ffill')
    pct = df.pct_change().dropna() #(how='all')
    riskpct = riskfree.pct_change().dropna()
    mean = pd.DataFrame(pct.mean(),columns=['Mean'],index=pct.columns)
    mean_rf = mean - riskpct.mean()
    std = pd.DataFrame(pct.std(),columns=['Std'],index=pct.columns)
    numerator = pct.sub(riskpct,axis=0)
    downside_risk = ((numerator[numerator<0].fillna(0))**2).mean()
    noa = len(df.columns)
    weigths = np.random.random(noa)
    weigths /= np.sum(weigths)
    observations = len(df.index)
    mean_returns = df.pct_change().mean()
    cov = df.pct_change().cov()
    alpha = 0.1
    rf = riskpct.mean()
    num_portfolios = 1000
    Upbound = 0.075
    result = [df,riskfree,pct,riskpct,mean,mean_rf,std,numerator,downside_risk,noa,weigths\
        ,observations,mean_returns,cov,alpha,rf,num_portfolios,Upbound]
    return result

def CANADA():
    canada = pd.read_html("https://topforeignstocks.com/indices/the-components-of-the-sptsx-composite-index/")[0]
    canada = list(canada.Ticker.values)
    freeRisk = '^GSPTSE'
    df = yahoo.download(canada,period="1y")["Adj Close"].fillna(method="ffill")
    pct = df.pct_change()#.dropna()
    mean = pd.DataFrame(pct.mean(),columns=['Mean'],index=pct.columns)
    riskpct = mean.mean()
    mean_rf = mean - riskpct.mean()
    std = pd.DataFrame(pct.std(),columns=['Std'],index=pct.columns)
    sharpe_ratio = pd.DataFrame(mean_rf['Mean']/(std['Std']), columns=['SharpeRatio'],index=pct.columns)
    orderedsharpe = sharpe_ratio.sort_values('SharpeRatio', axis=0, ascending=False)
    lista = list(orderedsharpe.head(50).index.values)
    df = yahoo.download(lista,period="1y",interval="60m")["Adj Close"].fillna(method="ffill")
    riskfree = yahoo.download(freeRisk, period="1y",interval="60m")['Adj Close'].fillna(method='ffill')
    pct = df.pct_change().dropna() #(how='all')
    riskpct = riskfree.pct_change().dropna()
    mean = pd.DataFrame(pct.mean(),columns=['Mean'],index=pct.columns)
    mean_rf = mean - riskpct.mean()
    std = pd.DataFrame(pct.std(),columns=['Std'],index=pct.columns)
    numerator = pct.sub(riskpct,axis=0)
    downside_risk = ((numerator[numerator<0].fillna(0))**2).mean()
    noa = len(df.columns)
    weigths = np.random.random(noa)
    weigths /= np.sum(weigths)
    observations = len(df.index)
    mean_returns = df.pct_change().mean()
    cov = df.pct_change().cov()
    alpha = 0.1
    rf = riskpct.mean()
    num_portfolios = 1000
    Upbound = 0.075
    result = [df,riskfree,pct,riskpct,mean,mean_rf,std,numerator,downside_risk,noa,weigths\
        ,observations,mean_returns,cov,alpha,rf,num_portfolios,Upbound]
    return result

def FTSE():
    england = pd.read_html("https://topforeignstocks.com/indices/components-of-the-ftse-100-index/")[0]
    england = list(england.Ticker.values)
    freeRisk = '^FTSE'
    df = yahoo.download(england,period="1y")["Adj Close"].fillna(method="ffill")
    pct = df.pct_change()#.dropna()
    mean = pd.DataFrame(pct.mean(),columns=['Mean'],index=pct.columns)
    riskpct = mean.mean()
    mean_rf = mean - riskpct.mean()
    std = pd.DataFrame(pct.std(),columns=['Std'],index=pct.columns)
    sharpe_ratio = pd.DataFrame(mean_rf['Mean']/(std['Std']), columns=['SharpeRatio'],index=pct.columns)
    orderedsharpe = sharpe_ratio.sort_values('SharpeRatio', axis=0, ascending=False)
    lista = list(orderedsharpe.head(50).index.values)
    df = yahoo.download(lista,period="1y",interval="60m")["Adj Close"].fillna(method="ffill")
    riskfree = yahoo.download(freeRisk, period="1y",interval="60m")['Adj Close'].fillna(method='ffill')
    pct = df.pct_change().dropna() #(how='all')
    riskpct = riskfree.pct_change().dropna()
    mean = pd.DataFrame(pct.mean(),columns=['Mean'],index=pct.columns)
    mean_rf = mean - riskpct.mean()
    std = pd.DataFrame(pct.std(),columns=['Std'],index=pct.columns)
    numerator = pct.sub(riskpct,axis=0)
    downside_risk = ((numerator[numerator<0].fillna(0))**2).mean()
    noa = len(df.columns)
    weigths = np.random.random(noa)
    weigths /= np.sum(weigths)
    observations = len(df.index)
    mean_returns = df.pct_change().mean()
    cov = df.pct_change().cov()
    alpha = 0.1
    rf = riskpct.mean()
    num_portfolios = 1000
    Upbound = 0.075
    result = [df,riskfree,pct,riskpct,mean,mean_rf,std,numerator,downside_risk,noa,weigths\
        ,observations,mean_returns,cov,alpha,rf,num_portfolios,Upbound]
    return result

def AUSTRALIA():
    australia = pd.read_html("https://topforeignstocks.com/indices/components-of-the-s-p-asx-all-australian-200-index/")[0]
    aussie = list(australia['Ticker'].values)
    freeRisk = '^AXJO'
    df = yahoo.download(aussie,period="1y")["Adj Close"].fillna(method="ffill")
    pct = df.pct_change()#.dropna()
    mean = pd.DataFrame(pct.mean(),columns=['Mean'],index=pct.columns)
    riskpct = mean.mean()
    mean_rf = mean - riskpct.mean()
    std = pd.DataFrame(pct.std(),columns=['Std'],index=pct.columns)
    sharpe_ratio = pd.DataFrame(mean_rf['Mean']/(std['Std']), columns=['SharpeRatio'],index=pct.columns)
    orderedsharpe = sharpe_ratio.sort_values('SharpeRatio', axis=0, ascending=False)
    lista = list(orderedsharpe.head(50).index.values)
    df = yahoo.download(lista,period="1y",interval="60m")["Adj Close"].fillna(method="ffill")
    riskfree = yahoo.download(freeRisk, period="1y",interval="60m")['Adj Close'].fillna(method='ffill')
    pct = df.pct_change().dropna() #(how='all')
    riskpct = riskfree.pct_change().dropna()
    mean = pd.DataFrame(pct.mean(),columns=['Mean'],index=pct.columns)
    mean_rf = mean - riskpct.mean()
    std = pd.DataFrame(pct.std(),columns=['Std'],index=pct.columns)
    numerator = pct.sub(riskpct,axis=0)
    downside_risk = ((numerator[numerator<0].fillna(0))**2).mean()
    noa = len(df.columns)
    weigths = np.random.random(noa)
    weigths /= np.sum(weigths)
    observations = len(df.index)
    mean_returns = df.pct_change().mean()
    cov = df.pct_change().cov()
    alpha = 0.1
    rf = riskpct.mean()
    num_portfolios = 1000
    Upbound = 0.075
    result = [df,riskfree,pct,riskpct,mean,mean_rf,std,numerator,downside_risk,noa,weigths\
        ,observations,mean_returns,cov,alpha,rf,num_portfolios,Upbound]
    return result

def binance():
    binance = pd.read_html('https://coinmarketcap.com/exchanges/binance/')[0]
    coins =  list(filter(lambda x: (x[-5:] == '/USDT'), binance.Pair.to_list()))
    coins = [i.replace('/USDT','-USD') for i in coins]
    df = yahoo.download(coins,period="1y")["Adj Close"].fillna(method="ffill")
    freeRisk = df.T.mean() # self-generated, as using Bitcoin as benchmark is a possibility but will bias the result
    pct = df.pct_change()
    mean = pd.DataFrame(pct.mean(),columns=['Mean'],index=pct.columns)
    riskpct = mean.mean()
    mean_rf = mean - riskpct.mean()
    std = pd.DataFrame(pct.std(),columns=['Std'],index=pct.columns)
    sharpe_ratio = pd.DataFrame(mean_rf['Mean']/(std['Std']), columns=['SharpeRatio'],index=pct.columns)
    orderedsharpe = sharpe_ratio.sort_values('SharpeRatio', axis=0, ascending=False)
    lista = list(orderedsharpe.head(30).index.values)
    df = yahoo.download(lista,period="1y",interval="60m")["Adj Close"].fillna(method="ffill")
    riskfree = df.T.mean().fillna(method='ffill')
    pct = df.pct_change().dropna() #(how='all')
    riskpct = riskfree.pct_change().dropna()
    mean = pd.DataFrame(pct.mean(),columns=['Mean'],index=pct.columns)
    mean_rf = mean - riskpct.mean()
    std = pd.DataFrame(pct.std(),columns=['Std'],index=pct.columns)
    numerator = pct.sub(riskpct,axis=0)
    downside_risk = ((numerator[numerator<0].fillna(0))**2).mean()
    noa = len(df.columns)
    weigths = np.random.random(noa)
    weigths /= np.sum(weigths)
    observations = len(df.index)
    mean_returns = df.pct_change().mean()
    cov = df.pct_change().cov()
    alpha = 0.1
    rf = riskpct.mean()
    num_portfolios = 1000
    Upbound = 0.075
    result = [df,riskfree,pct,riskpct,mean,mean_rf,std,numerator,downside_risk,noa,weigths\
        ,observations,mean_returns,cov,alpha,rf,num_portfolios,Upbound]
    return result
