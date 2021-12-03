#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 21 16:39:28 2021

@author: lorenzo
"""

import urllib.request
import pandas as pd
import datetime as dt 
import yfinance as yahoo
import matplotlib.pyplot as plt 
from pylab import mpl
mpl.rcParams['font.family'] = 'serif'
plt.style.use('fivethirtyeight')

today = dt.date.today()

url = 'https://www.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/seriese.xls'
u = urllib.request.urlretrieve(url, 'seriese.xls')

# Sheetnames of seriese.xls available at the link url
# ['BASE MONETARIA', 'RESERVAS','DEPOSITOS','PRESTAMOS','TASAS DE MERCADO',
# 'INSTRUMENTOS DEL BCRA', 'NOTAS']
# download the sheets and clean the data
basem = pd.read_excel(u[0], sheet_name='BASE MONETARIA')
reservas = pd.read_excel(u[0], sheet_name='RESERVAS')
depositos = pd.read_excel(u[0], sheet_name='DEPOSITOS')
#prestamos = pd.read_excel(u[0], sheet_name='PRESTAMOS')
#tasas = pd.read_excel(u[0], sheet_name='TASAS DE MERCADO')
instrumentos = pd.read_excel(u[0], sheet_name='INSTRUMENTOS DEL BCRA')
#notas = pd.read_excel(u[0], sheet_name='NOTAS'

discardBASEM = []
for i in range(len(basem)):
    if type(basem.iloc[i,0]) != type(basem.iloc[8,0]):
        discardBASEM.append(i)
    else:
        pass
        
interval = [(max(discardBASEM[:8]))+1,min(discardBASEM[8:])]
basem = basem.iloc[interval[0]:interval[1]]
monetaria = pd.DataFrame(basem.iloc[:,24].values,columns=['billete_publico'],index=basem.iloc[:,0].values)
start = dt.datetime(2011,9,1)
start_date = monetaria.loc[start:].head(1).index.values[0]
end_date = monetaria.index[-1]

# Take every monetary aggregate
monetaria['billete_privado'] = basem.iloc[:,25].values
monetaria['circulante'] = monetaria['billete_publico'] + monetaria['billete_privado']
monetaria['cta_cte_bcra'] = basem.iloc[:,27].values
monetaria['total_base'] = monetaria['billete_privado'] + monetaria['billete_publico'] + monetaria['cta_cte_bcra']
monetaria = monetaria.loc[start_date:end_date]
length = len(monetaria) # extent of how long the series you want it to be. global variable 

data = monetaria.total_base.groupby([monetaria.index.year,monetaria.index.month]).mean()
data = data.rename_axis(['year','month']).reset_index()
data['day'] = 1
data.index = pd.to_datetime(data[['year','month','day']]).dt.strftime('%Y-%m-%d')

data = data[['total_base']]

emision = monetaria.total_base.groupby([monetaria.index.year]).mean()

emision = pd.DataFrame(emision.values,columns=['Emisión'],index=emision.index)
    
macro = yahoo.download("ARS=X YPFD.BA YPF",start="2001-09-01",end="2021-09-01")["Adj Close"].fillna(method="ffill")
macro['YPF-Mercado'] = macro['YPFD.BA'] / macro['YPF']
macro['1-Price-Break'] = (macro['YPF-Mercado'] / macro['ARS=X']) - 1.0

peso = macro[['ARS=X','YPF-Mercado']]
peso_anual = peso.groupby([peso.index.year]).mean()