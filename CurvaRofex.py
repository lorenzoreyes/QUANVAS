import urllib.request
import pandas as pd
import datetime as dt 
import yfinance as yahoo
import matplotlib.pyplot as plt
import ssl, random, glob
import urllib.request

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context
    #from pytickersymbols import PyTickerSymbols #https://pypi.org/project/pytickersymbols/

hoy = dt.date.today().strftime('%d-%m-%Y')

destino = list(glob.glob("/home/lorenzo/Desktop/Akira/Chartboard/Curva/*"))
destino.sort()
ayer = pd.read_csv(f'{destino[-2]}')

rofex = pd.read_html('https://www.rofex.com.ar/cem/Spot.aspx')
cierre = pd.read_html('https://www.rofex.com.ar/cem/Cierre.aspx')
cierre = cierre[7].iloc[:11,:]

dolar35 = (rofex[7].iloc[0,2] / 10000.0)

close = pd.DataFrame(cierre.iloc[:,:2].values,columns=[['Futuro','Anterior']],index=range(len(cierre)))
dia = dt.date.today() # - dt.timedelta(1)
close[f"{dia.strftime('%d/%m/%y')}"] = cierre['Ajuste']
close[f"{dia.strftime('%d/%m/%y')}"] = close[f"{dia.strftime('%d/%m/%y')}"] / 10000.0
close['Anterior'] =  close['Anterior'] / 10000.0
close['Variación'] = close.iloc[:,2].values - close.iloc[:,1].values
close['Variación%'] = ((close.iloc[:,2].values / close.iloc[:,1].values) - 1) * 100.0
close['Volumen'] = cierre['Volumen'] * 1000
close['Total Volumen'] = cierre['Volumen'] * 1000 / (cierre['Volumen'] * 1000).sum()
close['Interés Abierto'] = cierre['IA'].to_list() #[int(j) for j in [i.replace('.','') for i in cierre['IA'].to_list()]]
close['Total Int. Ab.'] =  close['Interés Abierto'] / close['Interés Abierto'].sum()


mae = pd.read_html('https://servicios.mae.com.ar/mercados/Forex/Default.aspx')

spot = mae[7].Quote.values[0]

caduca = []#.strftime('%Y-%m-%d')]
for i in range(len(close)):
    caduca.append((pd.date_range(dt.date.today().strftime('%Y-%m-%d'),periods=len(close),freq='BM')[i]))

vencimiento = []
for i in range(len(close)):  
  vencimiento.append(dt.datetime.strptime(str(caduca[i])[2:10],('%y-%m-%d')))

vence = [i.days for i in [i - (dt.datetime.today() - dt.timedelta(1)) for i in vencimiento]]
close['dias'] = vence 
close['dias'] = close['dias'] 

close['TNA'] = ((close[f"{dia.strftime('%d/%m/%y')}"].values / spot)-1) * (365 / close['dias'].values)
tasa = [j + '%' for j in [str(i) for i in list(ayer.iloc[:,10])]]
close['TNA Ant'] = tasa[1:]
close['TEA'] = ((1 + (((close['TNA'].values)) * (close['dias'].values / 365))) ** (365 / close['dias'].values)) - 1.0
close['TNA 30d'] = ((1 + close['TEA'].values) ** (1 / 12) - 1) * 12
close = close.fillna(value=0)
close['TNA Ant'] = [float(j) for j in [i.replace('%','') for i in list(close.iloc[:,-3].values)]]
close['TNA'],close['TNA 30d'],close['TEA'] = close['TNA']*100,close['TNA 30d']*100,close['TEA']*100
close.iloc[:,-4:] = round(close.iloc[:,-4:],2)
#close['Anterior'] = ayer.iloc[:,2].values
close.index =  vencimiento

enlista = list(filter(lambda x: (x[0:3] == 'DLR'),close.iloc[:,0].values))

recorte = pd.DataFrame(columns=close.columns)

for i in range(len(enlista)):
    recorte = recorte.append((close[close.Futuro.values==enlista[i]]))

close = recorte

mes = []
for i in range(len(close)):
    mes.append(dt.datetime.strptime(list(close.iloc[:,0])[i][3:],('%m%Y')))

mes = [i.strftime('%b-%y') for i in mes]

close.index = mes

close = close.rename(columns={'Anterior':f'{ayer.columns[2]}'})
y = close.index 
x = close['TNA'].values
z = close['TNA Ant'].values
#tabla = tabla.rename(columns={f'TasaImplicita':f'Promedio Tasa {round(promedio.values[0],2)}%'})
plt.subplots(figsize=(15,10))
plt.scatter(y,x,s=600, cmap='RdYlBu')
plt.scatter(y,z,s=600, cmap='RdYlBu')
plt.grid()
plt.title(f'Curva de TNA {str(close.columns.values[2])[2:10]} y {str(close.columns.values[1])[2:10]} Dolar', fontsize=30, fontweight='bold')
plt.plot(y, x, '-o')
plt.plot(y, z, '-o')
plt.xticks(size = 20)
plt.yticks(size = 20)
plt.savefig('/home/lorenzo/Desktop/Akira/Chartboard/curvadolar.png',dpi=300)

close = round(close,4)
fila1 = pd.DataFrame([['Spot MAE'] + ['']  + [spot] + ([''] * (len(close.columns) -3))])
#fila2 = pd.DataFrame([['DBCRA3500'] + ['']  + [dolar35] + ([''] * (len(close.columns) -3))])

fila1 = pd.DataFrame(fila1.values,columns=close.columns)
close = fila1.append(close)
viejo = list((ayer.iloc[:,2]).values)[0]
ayer = list(close.iloc[:,1])
ayer[0] = viejo
close.iloc[:,1] = ayer #+ list(close.iloc[:,1].values[2:])

close.to_csv(f'/home/lorenzo/Desktop/Akira/Chartboard/Curva/CurvaRofex {hoy}.csv',index=False)
