# Same script as scanner.py, but parsing old excel
# we have to notify via email to the client that the operation
# had been done and paste the new scenario they are in.
import os, shutil, glob 
import pandas as pd, numpy as np
import datetime as dt


file = []

for filename in glob.iglob('/home/lorenzo/Quanvas/Maintenance/*'):
    file.append(filename)

csv = pd.DataFrame(file,columns=['Path'])

csv['Action'] = [i.split('/')[-1].split()[0] for i in csv.Path.to_list()]
csv['oldCapital'] = [i.split('/')[-1].split()[1] for i in csv.Path.to_list()]
csv['Symbol'] = [i.split('/')[-1].split()[2] for i in csv.Path.to_list()]
csv['Name'] = [' '.join(i.split('/')[-1].split()[3:5]) for i in csv.Path.to_list()]
csv['Email'] = [i.split('/')[-1].split()[5] for i in csv.Path.to_list()]
csv['Capital'] = [i.split('/')[-1].split()[6] for i in csv.Path.to_list()]
csv['Optimization'] = [i.split('/')[-1].split()[7] for i in csv.Path.to_list()]
csv['Date'] = [i.split('/')[-1].split()[8].split('.')[0] for i in csv.Path.to_list()]
csv['Change'] = csv.Capital.values.astype(int) - csv.oldCapital.values.astype(int)
#csv['Withdraw'] = [i.split('/')[-1].split()[9].split('.')[0] for i in csv.Path.to_list()]
csv['NewName'] =['/'.join(i.split('/')[:-1]) + '/' + ' '.join(i.split('/')[-1].split(' ')[2:-1]) + '.xlsx' for i in csv.Path.to_list()]
# excel to iterate to send emails
csv.index = range(len(csv))

csv.to_csv('/home/lorenzo/Quanvas/maintain.csv',index=False)
