import pandas as pd, numpy as np 
import datetime as dt
from scanner import * # refresh active clients

""" Test excel with inputs to be taken by script macro.py
  Columns
  Names = Name + Surname
  Emails = email to contact
  Money = capital to invest
  Markets = Market to operate in 
  Symbol = Market Symbol
  Optimization = level of risk desired
  Status = [0,1,2,3] 0 do nothing, 1 update, 2 Change ammount, 3 Update Risk
  Change = Conditional value if Status == 2 to withdraw or deposit money
  Timestamp = Stamp the last operation made
  """
clients = csv[['Names','Symbol','Path']]
clients['PortfolioID'] = clients.index.values
clients = clients[['PortfolioID','Names','Symbol','Path']]

clients.to_csv('clients.csv',index=False)
