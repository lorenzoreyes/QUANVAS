import pandas as pd
import datetime as dt
import random
from faker import Faker

fake = Faker()

# lets generate a random client excel info
names = []
for _ in range(25):
    names.append(fake.name())
    
#  Pass it as a DataFrame
clients = pd.DataFrame(names,columns=['Names'],index=range(len(names)))

clients['Emails'] = ([i + '@gmail.com' for i in [i.replace(' ','') for i in names]])

money = []
for _ in range(len(clients)):
    money.append(random.randrange(100000,100000000,1))
    
clients['Money'] = money

mercados = ['GSPC','FTSE','NIKKEI','BOVESPA','CANADA','AUSTRALIA','Shanghai','Crypto']

markets = []
for _ in range(len(clients)):
    markets.append(random.randrange(0,8,1))

clients['Markets'] = markets
    
symbol = []
for i in range(len(clients)):
    symbol.append(mercados[clients.Markets[i]])
    
clients['Symbol'] = symbol

optimization = []
for _ in range(len(clients)):
    optimization.append(random.randrange(0,4,1))
    
clients['Optimization'] = optimization

status = []
for _ in range(len(clients)):
    status.append(random.randrange(0,4,1))
 
clients['Status'] = status

change = []
for i in range(len(clients)):
    if clients.Status.values[i] != 2:
        change.append(0)
    else:
        change.append(random.randrange(-10000000,100000000,1))
 

clients['Change'] = change


clients['TimeStamp'] = dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')


clients.to_csv('clients.csv',index=False)
