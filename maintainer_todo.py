# We want to iterate excels, perform a task and save changes
# designed in TrackUpdate.py Grab an input int 
# of excel to perform task (monitor, update, withdraw, etc)
# from the command line.

import pandas as pd

pd.options.display.float_format = '{:,.2f}'.format

database = pd.read_csv('scanner.csv')

# 1. Choose excel to work with and operation what operation to do
def portfolio_operation():
    name = input("\nWhat client Name do you want? ")
    client = (list(filter(lambda x: (name in x),database['Path'].to_list())))
    client = pd.DataFrame(client, columns=[f'{name} Found'],index=range(len(client)))
    print(client)
    order = int(input("\nType [N]umber for a portfolio to update Status \n\n"))
    index = (database.Path.to_list()).index(client[f'{name} Found'][order])
    state = int(input("\nType Status Command\n(0) to pass,\n(1) to update,\n(2) to change capital,\n(3) to reset risk.\n\n\t"))
    change = 0
    if state==2:
        change = int(input("\nSpecify capital to deposit or withdraw\n\n\t"))
    database.Status.values[index], database.Change.values[index] = int(state), int(change)
    database.to_csv('scanner.csv',index=False)
    
def trigger():
    portfolio_operation()
    question = (input("What you want to do? \n(1) Do another one, \n(2) Quit.\n\nDecide:  "))
    if question == '1':
     trigger()
    else:
     print('End todos') 
    
# final iterator of eternal loop. Save recommendation, do another operation or leave.
if __name__ =='__main__':
  trigger()

        
    