import os, shutil, glob 
import pandas as pd, numpy as np
import datetime as dt

# Taken the path to each file we break it down to obtain and iterate each value
# Names of the client (Name + Surname), Symbol of the market it operates
# Email (without .com, it will be added in each iteration)
# Capital as ammount of money invested
# Optimization Taken

file = []

for filename in glob.iglob('/home/lorenzo/Quanvas/DATABASE/*'):
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
file.index = range(len(file))

file.to_csv('/home/lorenzo/Quanvas/scanner.csv',index=False)
