# We want to iterate excels, perform a task and save changes
# designed in TrackUpdate.py Grab an input int 
# of excel to perform task (monitor, update, withdraw, etc)
# from the command line.

import pandas as pd, numpy as np, glob
import yfinance as yahoo, datetime as dt
import trackCLI as tracker
import os, shutil

pd.options.display.float_format = '{:,.2f}'.format

# 1. Want to generate a dictionary key:val ID:name to pick file
# As this every time re run the code the list is updated
def print_database():
    file = []
    clientDict = {}

    for filename in glob.iglob('./DATABASE/*'):
      file.append(filename)
      clientDict = dict(map(reversed, enumerate(file)))  
      clientDict = dict((v,k) for k,v in clientDict.items())

    clientDict = pd.DataFrame(clientDict.items(), columns=['IDs','Path'])
    clientDict = clientDict.sort_values('Path',axis=0,ascending=True)
    clientDict['IDs'] = range(len(clientDict))
    clientDict.index = range(len(clientDict))
    return clientDict


# 2. Choose excel to work with and operation what operation to do
def portofolio_operation():
    database = (print_database())
    #print(database)
    database = database.Path.to_list()
    name = input("\nWhat client Name do you want? ")
    client = (list(filter(lambda x: (name in x),database)))
    client = pd.DataFrame(client, columns=[f'{name} Portfolios'],index=range(len(client)))
    print(client)
    order = int(input("\nType [N]umber for a portfolio, else to do something else \n\n"))
    if type(order) == int:
        data = pd.read_excel(client[f'{name} Portfolios'][order])
    else:
        database = (print_database()).Path.to_list()
        name = input("What client Name do you want? ")
        client = (list(filter(lambda x: (name in x),database)))
        client = pd.DataFrame(client, columns=[f'{name} Portfolios'],index=range(len(client)))
        print(client)
        order = int(input("[N]umber for a portfolio, else to do something else \n"))
    
    print(f"What task do you want to do to {client[f'{name} Portfolios'][order]} ?:\n(1) Monitor Portfolio? To watch performance.\n(2) Do a Deposit or Withdraw? Specify the ammount of capital to change.\n(3) Update risk? By adding new information.\n\n")
    action = int(input("Type your Task: ...  "))
    if action == 1:
      data = tracker.PortfolioMonitor(data)
    elif action == 2:
      data = tracker.DepositOrWithdraw(data)
    elif action == 3:
      data = tracker.portfolioRiskUpdated(data)
    #lista = [data,f'{database.Path[request]}', request]
    lista = [data,f'{client[f"{name} Portfolios"][order]}',order]
    return lista # data saved as a list because we can track name of the client to further save

# 3. Print it out. Make a decisition, (a) save and do something else, (b) don't save and do something else or (c) quit.
def operation():
  action = portofolio_operation() # call function
  excel, name, request = action[0].copy(), action[1], action[2]
  print(excel)
  print(f"Accumulated Return of\n{name} is\n[{excel.PnLpercent.values[0] - 1 :.4%}]".center(50,'_'))
  question = (input("What you want to do? \n(1) Save and do something else, \n(2) Don't save, do something else \nOr (3) Quit.\n\nDecide:  "))
  if question == '1':
      basics = excel.copy()
      folder = os.makedirs('Oldportfolios',exist_ok=True)
      old = name.replace('./DATABASE/','Oldportfolios/')
      shutil.move(f'{name}',f'{old}')
      basics = tracker.BacktoBasics(basics)
      filename = ' '.join(name.split('/')[-1].split()[:-1])
      sheet = filename + ' ' + str(dt.date.today())
      new = os.makedirs('Updated',exist_ok=True)
      path = './Updated/' + sheet
      writer = pd.ExcelWriter(f'{path}.xlsx', engine='xlsxwriter')
      basics.to_excel(writer, sheet_name=str(dt.date.today()))
      excel.to_excel(writer,sheet_name='change made, old New')
      writer.save()
      operation()
  elif question == '2':
      operation()
  elif type(question) != ('1' or '2'):
      print("See ya next time buddy")

# final iterator of eternal loop. Save recommendation, do another operation or leave.
if __name__ =='__main__':
  operation()
  
