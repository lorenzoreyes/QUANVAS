import urllib.request
import pandas as pd
import datetime as dt 
import yfinance as yahoo
import matplotlib.pyplot as plt
import ssl, random, glob
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
    
rofex = pd.read_html('http://datacenter.matba.com.ar/ajustesdc.aspx')

tabla = rofex[16]
tabla = tabla.iloc[:,2:]
tabla.columns = tabla.iloc[0,:].values
tabla = tabla.iloc[3:,:]
tabla = tabla.drop(['Aper.', 'Bajo', 'Alto', 'Ult.','Vol.','Vol. IRC','Var/O.I.', 'Mon'],axis=1)
tabla = tabla.rename(columns={"PosiciÃ³n":"Futuro"})