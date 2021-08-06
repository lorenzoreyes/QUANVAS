# This file aims to iterate portfolios listed in scanner.csv,
# perform the same operations of iteratEternity.py but using the 
# input excel as instructions to do opetations at scale.
# By changing scanner.csv we maintain the DATABASE updated.
# Reset format of excel with function BacktoBasiscs, so it can be re iterated in the future

import os, shutil
import yfinance as yahoo
import pandas as pd
import datetime as dt
import numpy as np
import trackATM as tracker 

# read the database and generate all portfolio at once
clients = pd.read_csv('scanner.csv')

for i in range(len(clients)):
    if clients.Status.values[i] == 0:
        pass
    elif clients.Status.values[i] == 1:
      # Update values of the portfolio
      name = path = str(clients['Path'][i])
      data = pd.read_excel(path)
      previous = data.copy()
      data = tracker.PortfolioMonitor(data)
      basics = data.copy()
      basics = tracker.BacktoBasics(basics)
      folder = os.makedirs('Oldportfolios',exist_ok=True)
      older = name.replace('./DATABASE/','./Oldportfolios/')
      shutil.move(f'{name}',f'{older}')
      newName = ' '.join(path.split()[:-1]) + ' ' + str(dt.date.today()) + '.xlsx'
      writer = pd.ExcelWriter(f'{newName}',engine='xlsxwriter')
      basics.to_excel(writer,sheet_name=f'Updated {dt.date.today()}')
      data.to_excel(writer,sheet_name=str(dt.date.today()))
      previous.to_excel(writer,sheet_name='Previous Composition')
      writer.save()
      clients.TimeStamp.values[i] = dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
      # Reset Status to 0 as there any changes pending to do
      clients.Status.values[i] = 0
    elif clients.Status.values[i] == 2:
      # Deposit or Withdraw an specific ammount
      name = path = str(clients['Path'][i])
      data = pd.read_excel(path)
      previous = data.copy()
      data = tracker.DepositOrWithdraw(data,clients.Change.values[i])
      basics = data.copy()
      basics = tracker.BacktoBasics(basics)
      folder = os.makedirs('Oldportfolios',exist_ok=True)
      old = name.replace('./DATABASE/','./Oldportfolios/')
      shutil.move(f'{name}',f'{old}')
      newName = ' '.join(path.split()[:-1]) + ' ' + str(dt.date.today()) + '.xlsx'
      writer = pd.ExcelWriter(f'{newName}',engine='xlsxwriter')
      basics.to_excel(writer,sheet_name=f"Changed {dt.date.today()}")
      data.to_excel(writer,sheet_name=str(dt.date.today()))
      previous.to_excel(writer,sheet_name='Previous Composition')
      writer.save()
      clients.TimeStamp.values[i] = dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
      # Reset Status to 0 as there any changes pending to do
      clients.Status.values[i] = 0
      clients.Change.values[i] = 0
    elif clients.Status.values[i] == 3:
      # Update risk levels by resetting Component-Value-at-Risk
      name = path = str(clients['Path'][i])
      data = pd.read_excel(path)
      previous = data.copy()
      data = tracker.portfolioRiskUpdated(data)
      basics = data.copy()
      basics = tracker.BacktoBasics(data)
      folder = os.makedirs('Oldportfolios',exist_ok=True)
      old = name.replace('./DATABASE/','./Oldportfolios/')
      shutil.move(f'{name}',f'{old}')
      newName = ' '.join(path.split()[:-1]) + ' ' + str(dt.date.today()) + '.xlsx'
      writer = pd.ExcelWriter(f'{newName}',engine='xlsxwriter')
      basics.to_excel(writer,sheet_name=f"Risk Update {dt.date.today()}")
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


clients.to_csv('scanner.csv',index=False)
