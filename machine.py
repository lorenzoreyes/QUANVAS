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

    for filename in glob.iglob('./DATABASE/*'):
      file.append(filename)
    
    file = pd.DataFrame(file,columns=['Path'])
    file['Symbol'] = [i.split()[0][2:].split('/')[-1] for i in file.Path.to_list()]
    file['Name'] = [' '.join(i.split()[1:3]) for i in file.Path.to_list()]
    file['Email'] = [(i.split()[3]) for i in file.Path.to_list()]
    file['Capital'] = [i.split()[4] for i in file.Path.to_list()]
    file['Optimization'] = [i.split()[5] for i in file.Path.to_list()]
    file['Status'] = 0
    file['Change'] = 0
    file['TimeStamp'] = [(i.split()[-1][0:10]) for i in file.Path.to_list()]
    return file

# 2. Choose excel to work with and operation what operation to do
def portfolio_operation():
    database = (print_database())    
    name = input("\nWhat client Name do you want? ")
    client = (list(filter(lambda x: (name in x),database['Path'].to_list())))
    client = pd.DataFrame(client, columns=[f'{name} Portfolios'],index=range(len(client)))
    print(client)
    order = (input("\nType [N]umber for a portfolio, else to do something else \n\n"))
    for i in range(1):
        if type(int(order)) == int:
            data = pd.read_excel(client[f'{name} Portfolios'][order])
        else:
            portfolio_operation()

portfolio_operation()