# This file aims to iterate portfolios listed in clientsTODO.csv,
# perform the same operations of iteratEternity.py but using the 
# input excel as instructions to do opetations at scale.
# By changing clientsTODO.csv we maintain the DATABASE updated.

import os, shutil
import yfinance as yahoo
import pandas as pd
import datetime as dt
import numpy as np
import trackATM as tracker 

# read the database and generate all portfolio at once
clients = pd.read_csv('clients.csv')

for i in range(len(clients)):
    if clients.Status.values[i] == 0:
        pass
    elif clients.Status.values[i] == 1:
      # Update values of the portfolio
      name = path = './DATABASE/' + str(clients['Path'][i])
      data = pd.read_excel(path)
      previous = data.copy()
      data = tracker.PortfolioMonitor(data)
      folder = os.makedirs('Oldportfolios',exist_ok=True)
      older = name.replace('./DATABASE/','./Oldportfolios/')
      shutil.move(f'{name}',f'{older}')
      newName = ' '.join(path.split()[:-1]) + ' ' + str(dt.date.today()) + '.xlsx'
      writer = pd.ExcelWriter(f'{newName}',engine='xlsxwriter')
      data.to_excel(writer,sheet_name=str(dt.date.today()))
      previous.to_excel(writer,sheet_name='Previous Composition')
      writer.save()
      clients.TimeStamp.values[i] = dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
      # Reset Status to 0 as there any changes pending to do
      clients.Status.values[i] = 0
    elif clients.Status.values[i] == 2:
      # Deposit or Withdraw an specific ammount
      name = path = './DATABASE/' + str(clients['Path'][i])
      data = pd.read_excel(path)
      previous = data.copy()
      data = tracker.DepositOrWithdraw(data,clients.Change.values[i])
      folder = os.makedirs('Oldportfolios',exist_ok=True)
      old = name.replace('./DATABASE/','./Oldportfolios/')
      shutil.move(f'{name}',f'{old}')
      newName = ' '.join(path.split()[:-1]) + ' ' + str(dt.date.today()) + '.xlsx'
      writer = pd.ExcelWriter(f'{newName}',engine='xlsxwriter')
      data.to_excel(writer,sheet_name=str(dt.date.today()))
      previous.to_excel(writer,sheet_name='Previous Composition')
      writer.save()
      clients.TimeStamp.values[i] = dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
      # Reset Status to 0 as there any changes pending to do
      clients.Status.values[i] = 0
      clients.Money.values[i] = clients.Money.values[i] + clients.Change.values[i]
      clients.Change.values[i] = 0
    elif clients.Status.values[i] == 3:
      # Update risk levels by resetting Component-Value-at-Risk
      name = path = './DATABASE/' + str(clients['Path'][i])
      data = pd.read_excel(path)
      previous = data.copy()
      data = tracker.portfolioRiskUpdated(data)
      folder = os.makedirs('Oldportfolios',exist_ok=True)
      old = name.replace('./DATABASE/','./Oldportfolios/')
      shutil.move(f'{name}',f'{old}')
      newName = ' '.join(path.split()[:-1]) + ' ' + str(dt.date.today()) + '.xlsx'
      writer = pd.ExcelWriter(f'{newName}',engine='xlsxwriter')
      data.to_excel(writer,sheet_name=str(dt.date.today()))
      previous.to_excel(writer,sheet_name='Previous Composition')
      writer.save()
      clients.TimeStamp.values[i] = dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
      # Reset Status to 0 as there any changes pending to do
      clients.Status.values[i] = 0
  
to_delete = list(filter(lambda i: (i[0:3] == 'Unn'),clients.columns.to_list()))

for i in range(len(to_delete)):
    if to_delete[i] in clients.columns.to_list():
        del clients[f'{to_delete[i]}']


clients.to_csv('clients.csv',index=False)
