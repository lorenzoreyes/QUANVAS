import pyRofex
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
from pylab import mpl
mpl.rcParams['font.family'] = 'serif'
plt.style.use('fivethirtyeight')

# initialize API Connection
'''
pyRofex.initialize(user="lreyes3394",
                   password="neepjZ4!",
                   account="REM3394",
                   environment=pyRofex.Environment.REMARKET)
'''
pyRofex.initialize(user="MD_REYES",
                   password="Lorenzo6+",
                   account="88406W",
                   environment=pyRofex.Environment.LIVE)

# make a list of all available month from current to 12 forwards
hoy = dt.date.today()
fechas = []
for i in range(10): #Changed to 10 as 12 sometimes dont have data
    if (hoy.month + i) > 12:
        fechas.append(dt.date(hoy.year+1,(hoy.month+i-12),1))
    else:
        fechas.append(dt.date(hoy.year,hoy.month+i,1)) 

# create proper tickets as a dictionary        
meses = {1:'ENE',2:'FEB',3:'MAR',4:'ABR',5:'MAY',6:'JUN',7:'JUL',8:'AGO',9:'SEP',10:'OCT',11:'NOV',12:'DIC'}
str(hoy.year)[-2:]
tickets = []
for i in range(len(fechas)):
  tickets.append('DLR/' + meses[(fechas[i]).month] + str((fechas[i]).year)[-2:])

    #tickets.append('DO' + meses[(fechas[i]).month] + str((fechas[i]).year)[-2:])

end = dt.date.today()
#start = end - dt.timedelta(90) 
start = dt.date(2021,1,1)

# iterate the download
futuros = tickets.copy()

response = pyRofex.get_all_instruments()

#res = response['instruments']
#rows = []
#for i in range(len(response['instruments'])):
#    rows.append(f'{res[i]}'.split("'")[9])

for inst in response['instruments']:
    futuros.append(inst['instrumentId']['symbol'])

contratos = pd.DataFrame(futuros,columns=['Contratos'],index=range(len(futuros)))



for i in range(len(tickets)):
    print(f'Is {tickets[i]} a valid instrument? {tickets[i] in futuros}')
    

for i in range(len(tickets)):
    historic_trades = pyRofex.get_trade_history(tickets[i], start_date=start, end_date=end)
    trades = pd.DataFrame(historic_trades['trades']) # get dataframe from trades dictionary
    asset = pd.DataFrame(trades.price.values,columns=[f'{futuros[i]}'],index=trades.datetime)    
    indice = []
    for j in range(len(asset.index)):
        indice.append(dt.datetime.strptime(asset.index[j],('%Y-%m-%d %H:%M:%S.%f')))
    asset.index = indice
    asset = asset.groupby([asset.index.year,asset.index.month,asset.index.day,asset.index.hour,asset.index.minute]).mean()
    futuros[i] = asset

# concatenate all dataframes and sort index so no information get deleted
dolar = pd.concat([futuros[0],futuros[1],futuros[2],futuros[3],futuros[4],futuros[5],futuros[6]\
                   ,futuros[7],futuros[8],futuros[9]]).sort_index()#,futuros[10]]).sort_index() #futuros[11]]).sort_index()

dolar = dolar.fillna(method='ffill')    

# handle multi-index to single
dolar = dolar.rename_axis(['year','month','day','hour','minute']).reset_index()
dolar.index = pd.to_datetime(dolar[['year','month','day','hour','minute']]).dt.strftime('%Y-%m-%d %H:%M')
dolar = dolar.iloc[:,5:]

# download USD/ARS spot from Rofex CEM (Only available via web)
spot = pd.read_fwf('/home/lorenzo/Downloads/SpotROFEX.xls')
spot = spot.iloc[2:-7]
spot.iloc[:,0] = [i[:10] for i in spot.iloc[:,0].to_list()]
spot.index = spot.iloc[:,0]
spot['Spot'] = [float(j) for j in [i.replace(',','.') for i in spot['Unnamed: 4'].to_list()]]
spot = pd.DataFrame(spot.Spot.values,columns=['Spot'],index=spot.index)
indice = []
for j in range(len(spot.index)):
    indice.append((dt.datetime.strptime(spot.index[j],('%d/%m/%Y'))).strftime('%Y-%m-%d %H:%M:%S.%f'))

spot.index = indice
spot = spot.sort_index(axis=0,ascending=True)
spot = spot.loc[f'{dolar.index[0][:10]}':]

# concat spot with the rest of the futures
dolar = pd.concat([spot,dolar]).sort_index()

dolar = dolar.fillna(method='ffill')

cierre = dolar.copy()
columnas = []
for i in range(len(cierre.columns)):
    columnas.append(str(cierre.columns[i]) + ' $' + str(round(cierre.iloc[-1,i],2)))

cierre.columns = columnas
cierre.index = [i[:10] for i in cierre.index.to_list()]
# close
fig = plt.figure(figsize=(30,15))
ax1 = fig.add_subplot(111)
cierre.iloc[:,0].plot(ax=ax1, lw=7., color='k')
cierre.iloc[:,1:].plot(ax=ax1, lw=5)
ax1.set_title('Spot & Futures Series', fontsize=50, fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=2)
ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=30)
plt.xticks(size=20)
plt.yticks(size=20)
plt.savefig('SpotnFutures.png',bbox_inches='tight')
Series = cierre.copy()

# return
cierre = dolar.pct_change().cumsum().copy() * 100.0
columnas = []
for i in range(len(cierre.columns)):
    columnas.append(str(cierre.columns[i]) + ' ' + str(round(cierre.iloc[-1,i],2)) + '%')

cierre.columns = columnas
cierre.index = [i[:10] for i in cierre.index.to_list()]
# cierre
fig = plt.figure(figsize=(30,15))
ax1 = fig.add_subplot(111)
cierre.iloc[:,0].plot(ax=ax1, lw=7., color='k')
cierre.iloc[:,1:].plot(ax=ax1, lw=5.)
ax1.set_title('Return of Spot & Futures', fontsize=50, fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=2)
ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=30)
plt.xticks(size=20)
plt.yticks(size=20)
plt.savefig('futuresReturn.png',bbox_inches='tight')

# remaining days to calculate implied rate
caduca = []#.strftime('%Y-%m-%d')]
for i in range(12):
    caduca.append((pd.date_range(dt.date.today().strftime('%Y-%m-%d'),periods=12,freq='BM')[i]))

vida = pd.DataFrame(0,columns=caduca,index=cierre.index)
vida.index = [pd.Timestamp(i) for i in vida.index.to_list()]
for i in range(len(vida.index)):
    for j in range(len(vida.columns)):
        vida[f'{vida.columns[j]}'] = (vida.columns[j] - vida.index).days

# Tasa Implícita
tasa_implicita = pd.DataFrame(0,columns=dolar.columns[1:],index=vida.index)
# 1- (Future/Spot)-1    2- X (365 / days_pending)
for i in range(len(tasa_implicita.columns)):
    tasa_implicita[f'{tasa_implicita.columns[i]}'] = ((dolar.iloc[:,i+1].values/ dolar.iloc[:,0].values) -1)
    tasa_implicita[f'{tasa_implicita.columns[i]}'] =  (tasa_implicita[f'{tasa_implicita.columns[i]}'] * (365 / vida.iloc[:,i].values)).values

tasa_implicita = tasa_implicita.sort_index(axis=0,ascending=True)

tea = pd.DataFrame(0,columns=dolar.columns[1:],index=vida.index)

for i in range(len(tea.columns)):
    tea[f'{tea.columns[i]}'] = ((1 + (((tasa_implicita.iloc[:,i].values)) * (vida.iloc[:,i].values / 365))) ** (365 / vida.iloc[:,i].values)) - 1.0

tea = tea.sort_index(axis=0,ascending=True)

tna30 = pd.DataFrame(0,columns=dolar.columns[1:],index=vida.index)
for i in range(len(tna30.columns)):
    tna30[f'{tna30.columns[i]}'] = ((1 + tea.iloc[:,i].values) ** (1 / 12) - 1) * 12

tna30 = tna30.sort_index(axis=0,ascending=True)

tasa = tasa_implicita.copy() * 100.0
columnas = []
for i in range(len(tasa.columns)):
    columnas.append(str(tasa.columns[i]) + ' ' + str(round(tasa.iloc[-1,i],2)) + '%')

tasa.columns = columnas
# cierre
fig = plt.figure(figsize=(30,15))
ax1 = fig.add_subplot(111)
tasa.iloc[:,0].plot(ax=ax1, lw=7., color='k')
tasa.iloc[:,1:].plot(ax=ax1, lw=5.)
ax1.set_title('Serie Tasa Implícita', fontsize=50, fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=2)
ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=30)
plt.xticks(size=20)
plt.yticks(size=20)
plt.savefig('rateImpl.png',bbox_inches='tight')

monthly = dt.date.today() - dt.timedelta(30)
monthly5 = dt.date.today() - dt.timedelta(25)
monthly = monthly.strftime('%Y-%m-%d')
table = pd.DataFrame(dolar.tail(1).T.values,columns=['Close'],index=dolar.tail(1).T.index)
table['30 days'] = dolar.loc[f'{monthly}':f'{monthly5}'].mean().values
#table['Variación'] = table.iloc[:,0] - table.iloc[:,1]
table['Percent'] = ((table.iloc[:,0] - table.iloc[:,1]) - 1)
table['Impl. Rate'] = [None] + (tasa_implicita.iloc[-1,:].to_list())
table['Previous Impl. Rate'] = [None] + (tasa_implicita.loc[f'{monthly}':f'{monthly5}'].mean().to_list())
table['Effective Annual Rate'] = [None] + (tea.iloc[-1,:].to_list())
table['Impl. Rate 30d'] = [None] + (tna30.iloc[-1,:].to_list())
# SAVE table to inform futures scenario
table.to_csv(f'Dollar Futures {hoy}.csv')


writer = pd.ExcelWriter(f'ArgentinaForex {hoy}.xlsx',engine='xlsxwriter')
Series.to_excel(writer,sheet_name='Spot & Futures')
tasa_implicita.to_excel(writer,sheet_name='Implied Rate')
tea.to_excel(writer, sheet_name='Annaul Eff. Rate')
tna30.to_excel(writer,sheet_name='Impl. R 30days')
writer.save()
