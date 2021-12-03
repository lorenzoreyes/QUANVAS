import pandas as pd, yfinance as yahoo, numpy as np

cartera = pd.read_excel('Cartera 432000378.xlsx',sheet_name='CARTERA - Rendimiento')

cartera.columns = cartera.iloc[0,:].values
cartera = cartera.drop(0)
lista = list(cartera['Ticker'][0:31].values)
lista.sort()

data = yahoo.download(lista,period="1y")["Adj Close"].fillna(method="ffill")

tablero = pd.DataFrame(data.tail(1).T.values,columns=['Precio'],index=data.columns)

tablero['SMA30'] = data.rolling(round((len(data)/12)),min_periods=1).mean().tail(1).T.values
tablero['SMA90'] = data.rolling(round((len(data)/4)),min_periods=1).mean().tail(1).T.values
tablero['SMA180'] = data.rolling(round((len(data)/2)),min_periods=1).mean().tail(1).T.values
tablero['SMA1Y'] = data.rolling(round((len(data))),min_periods=1).mean().tail(1).T.values

