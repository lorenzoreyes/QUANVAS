import os, shutil, glob 
import pandas as pd, numpy as np
import datetime as dt


file = []

for filename in glob.iglob('/home/lorenzo/Quanvas/DATABASE/*'):
    file.append(filename)

csv = pd.DataFrame(file,columns=['Path'])

# Taken the path to each file we break it down to obtain and iterate each value
# Names of the client (Name + Surname), Symbol of the market it operates
# Email (without .com, it will be added in each iteration)
# Capital as ammount of money invested
# Optimization Taken

csv['Symbol'] = [i.split()[0][2:].split('/')[-1] for i in csv.Path.to_list()]
csv['Name'] = [' '.join(i.split()[1:3]) for i in csv.Path.to_list()]
csv['Email'] = [(i.split()[3]) for i in csv.Path.to_list()]
csv['Capital'] = [i.split()[4] for i in csv.Path.to_list()]
csv['Optimization'] = [i.split()[5] for i in csv.Path.to_list()]
csv['Status'] = 0
csv['Change'] = 0
csv['TimeStamp'] = dt.datetime.today().strftime('%H:%M:%S %d-%m-%Y')
csv.index = range(len(csv))

csv.to_csv('/home/lorenzo/Quanvas/scanner.csv',index=False)