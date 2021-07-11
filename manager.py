# We want to iterate excels, perform a task and save changes
# designed in TrackUpdate.py Grab an input int 
# of excel to perform task (monitor, update, withdraw, etc)
# from the command line.
# ITERATE FOLDERS

import pandas as pd, numpy as np, glob
import yfinance as yahoo, datetime as dt
import trackCLI as tracker
import os, shutil, re

pd.options.display.float_format = '{:,.2f}'.format

# 1. Want to generate a dictionary key:val ID:name to pick file
def print_database():
    folder = []
    clientDict = {}

    for foldername in glob.iglob('DATABASE/*'):
      folder.append(foldername)
   
      clientDict = dict(map(reversed, enumerate(folder)))  
      clientDict = dict((v,k) for k,v in clientDict.items())

    clientDict = pd.DataFrame(clientDict.items(), columns=['IDs','Excels'])
    clientDict = clientDict.sort_values('Excels',axis=0,ascending=True)
    clientDict['IDs'] = range(len(clientDict))
    clientDict.index = range(len(clientDict))
    return clientDict

# 2. Choose excel to work with and operation what operation to do
def portofolio_operation():
    database = print_database() # call print function
    print(database)
    request = int(input("Type the ID of your Client: "))
    data = pd.read_excel(database['Excels'][request])
    print(f"What task do you want to do to {database.Excels[request]} ?:\n(1) Monitor Portfolio? To watch performance.\n(2) Do a Deposit or Withdraw? Specify the ammount of capital to change.\n(3) Update risk? By adding new information.\n\n")
    action = int(input("Type your Task: ...  "))
    if action == 1:
      data = tracker.PortfolioMonitor(data)
    elif action == 2:
      data = tracker.DepositOrWithdraw(data)
    elif action == 3:
      data = tracker.portfolioRiskUpdated(data)
    lista = [data,f'{database.Excels[request]}']
    return lista # data saved as a list because we can track name of the client to further save

# 3. Print it out. Make a decisition, (a) save and do something else, (b) don't save and do something else or (c) quit.
def operation():
  action = portofolio_operation() # call function
  excel,name = action[0].copy(),action[1]
  print(excel)
  print(f"Accumulated Return of {name} is\n[{excel.PnLpercent.values[0] - 1 :.4%}]".center(50,'_'))
  question = str(input("What you want? \n(a) Save and do something else, \n(b) Don't save, do something else \nOr (c) Quit.\n\nDecide:  "))
  if question == 'a':
      basics = excel.copy()
      folder = os.makedirs('Oldportfolios',exist_ok=True)
      old = 'Oldportfolios/' + name.replace('excel/','')
      shutil.move(f'{name}',f'{old}')
      basics = tracker.BacktoBasics(basics)
      filename = re.findall(r"/[A-Za-z]+\s+\w+\s+\w+\+?", name)
      filename = filename[0]
      filename = filename.replace('/','')
      sheet = filename + ' ' + str(dt.date.today())
      path = './excel/' + sheet
      writer = pd.ExcelWriter(f'{path}.xlsx', engine='xlsxwriter')
      basics.to_excel(writer, sheet_name=str(dt.date.today()))
      excel.to_excel(writer,sheet_name='change made, old New')
      writer.save()
      operation()
  elif question == 'b':
      operation()
  else:
      print("See ya next time buddy")


# final iterator of eternal loop. Save recommendation, do another operation or leave.

if __name__ =='__main__':
  operation()
