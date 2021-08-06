# This file aims to iterate portfolios listed in scanner.csv,
# perform the same operations of iteratEternity.py but using the 
# input excel as instructions to do opetations at scale.
# By changing scanner.csv we maintain the DATABASE updated.
# Reset format of excel with function BacktoBasiscs, so it can be re iterated in the future

import pandas as pd, datetime as dt, numpy as np
import smtplib, re, os 
import credentials, glob 
import base64, shutil
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email import encoders
import trackATM as tracker
from templateReport import * # template html of all content of the email
#from scanner import *
import yfinance as yahoo 

file = []

for filename in glob.iglob('/home/lorenzo/Quanvas/DATABASE/*'):
    file.append(filename)

csv = pd.DataFrame(file,columns=['Path'])

# create a common dataframe with all tickets, to avoid
# downloading tickets per each client

lista = []
for i in range(len(csv)):
    index = pd.read_excel(csv.Path.values[i])
    index = index.iloc[:,0].to_list()
    lista += index
    lista = list(dict.fromkeys(lista))

data = yahoo.download(lista,period="252d",interval="60m")["Adj Close"].fillna(method="ffill")
clients = pd.read_csv('/home/lorenzo/Quanvas/scanner.csv')
hoy = dt.date.today().strftime('%d-%m-%Y')

for i in range(len(clients)):
    if clients.Status.values[i] == 0:
        pass
    elif clients.Status.values[i] == 1:
      # Update values of the portfolio
      cartera = pd.read_excel(csv.Path.values[i])
      previous = cartera.copy()
      path = str(clients['Path'][i])
      portfolio = pd.DataFrame(index=cartera.iloc[:,0]) 
      info = data.copy()
      update = []
      for j in range(len(portfolio)):
          update.append(info[f'{portfolio.index.values[j]}'].values[-1])
      portfolio = pd.DataFrame(index=cartera.iloc[:,0]) # rewrite
      portfolio['nominal'] = cartera['nominal'].values
      portfolio['pricePaid'] = cartera['price'].values
      portfolio['weights'] = (portfolio['nominal'] * portfolio['pricePaid']) / sum(portfolio['nominal'] * portfolio['pricePaid'])
      portfolio['notionalStart'] = sum(portfolio['nominal'] * portfolio['pricePaid'])
      portfolio['oldLiquidity'] = cartera['liquid'].values
      stocks = list(portfolio.index)
      portfolio['priceToday'] = update
      portfolio['notionalToday'] = sum(portfolio['priceToday'] * portfolio['nominal'])
      portfolio['PnLpercent'] = portfolio['notionalToday'] / portfolio['notionalStart']
      portfolio['PnLpercentEach'] = portfolio['priceToday'] / portfolio['pricePaid']
      # En nuevo nominal sumamos el resultado obtenido mas el remanente liquido para reinvertir, siendo nuestro total disponible
      portfolio['nominalNew'] = (portfolio['weights'] * (portfolio['notionalToday'] + portfolio['oldLiquidity']) // portfolio['priceToday']) # nuevo nominal
      portfolio['adjust'] = portfolio['nominalNew'] - portfolio['nominal'] # ajuste nominal
      portfolio['percentReb'] = (portfolio['nominalNew'] * portfolio['priceToday']) / sum(portfolio['nominalNew'] * portfolio['priceToday'])
      # Columnas vinculantes para conectar mes anterior con el proximo ya armado
      portfolio['notionalRebalance'] = sum(portfolio['nominalNew'] * portfolio['priceToday'])
      portfolio['liquidityToReinvest'] =  ((portfolio['notionalToday'] + portfolio['oldLiquidity']) - portfolio['notionalRebalance'])
      capital = int(portfolio.notionalToday.values[0] + portfolio.liquidityToReinvest.values[0])
      basics = portfolio.copy()
      basics = tracker.BacktoBasics(basics)
      folder = os.makedirs('Oldportfolios',exist_ok=True)
      name = path
      older = path.replace('./DATABASE/','./Oldportfolios/')
      shutil.move(f'{name}',f'{older}')
      newName = ' '.join(path.split()[:-1])
      newName = (path.split()[:-1])
      newName[-2] = str(capital)
      newName = ' '.join(newName) + ' ' + str(dt.date.today()) + '.xlsx'
      writer = pd.ExcelWriter(f'{newName}',engine='xlsxwriter')
      basics.to_excel(writer,sheet_name=f'Updated {dt.date.today()}')
      portfolio.to_excel(writer,sheet_name='Update Done')
      previous.to_excel(writer,sheet_name='Previous Composition')
      writer.save()
      clients.TimeStamp.values[i] = dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
      # Reset Status to 0 as there any changes pending to do
      clients.Status.values[i] = 0
    elif clients.Status.values[i] == 2:
      # Change capital ammount of the investment, positive or negative, satisfying original weights
      cartera = pd.read_excel(csv.Path.values[i])
      previous = cartera.copy()
      path = str(clients['Path'][i])
      portfolio = pd.DataFrame(index=cartera.iloc[:,0]) 
      info = data.copy()
      update = []
      for j in range(len(portfolio)):
          update.append(info[f'{portfolio.index.values[j]}'].values[-1])
      portfolio = pd.DataFrame(index=cartera.iloc[:,0]) # rewrite
      portfolio['nominal'] = cartera['nominal'].values
      portfolio['pricePaid'] = cartera['price'].values
      portfolio['weights'] = (portfolio['nominal'] * portfolio['pricePaid']) / sum(portfolio['nominal'] * portfolio['pricePaid'])
      portfolio['notionalStart'] = sum(portfolio['nominal'] * portfolio['pricePaid'])
      portfolio['oldLiquidity'] = cartera['liquid'].values
      portfolio['priceToday'] = update
      portfolio['notionalToday'] = sum(portfolio['priceToday'] * portfolio['nominal'])
      portfolio['PnLpercent'] = portfolio['notionalToday'] / portfolio['notionalStart']
      portfolio['PnLpercentEach'] = portfolio['priceToday'] / portfolio['pricePaid']
      portfolio['DepositOrWithdraw'] = float(clients.Change.values[i])
      portfolio['nominalNew'] = (portfolio['weights'] * ((portfolio['notionalToday'] + portfolio['oldLiquidity']) + portfolio['DepositOrWithdraw']) // portfolio['priceToday']) # nuevo nominal
      portfolio['adjust'] = portfolio['nominalNew'] - portfolio['nominal'] # ajuste nominal
      portfolio['percentReb'] = (portfolio['nominalNew'] * portfolio['priceToday']) / sum(portfolio['nominalNew'] * portfolio['priceToday'])
      portfolio['notionalRebalance'] = sum(portfolio['nominalNew'] * portfolio['priceToday'])
      portfolio['liquidityToReinvest'] =  ((portfolio['notionalToday'] +portfolio['oldLiquidity']))
      capital = int(portfolio.notionalToday.values[0] + portfolio.liquidityToReinvest.values[0])
      basics = portfolio.copy()
      basics = tracker.BacktoBasics(basics)
      folder = os.makedirs('Oldportfolios',exist_ok=True)
      name = path
      older = path.replace('./DATABASE/','./Oldportfolios/')
      shutil.move(f'{name}',f'{older}')
      newName = ' '.join(path.split()[:-1])
      newName = (path.split()[:-1])
      newName[-2] = str(capital)
      newName = ' '.join(newName) + ' ' + str(dt.date.today()) + '.xlsx'
      writer = pd.ExcelWriter(f'{newName}',engine='xlsxwriter')
      basics.to_excel(writer,sheet_name=f"Changed {dt.date.today()}")
      portfolio.to_excel(writer,sheet_name='Operation Change')
      previous.to_excel(writer,sheet_name='Previous Composition')
      writer.save()
      clients.TimeStamp.values[i] = dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
      # Reset Status to 0 as there any changes pending to do
      clients.Status.values[i] = 0
      clients.Change.values[i] = 0
    elif clients.Status.values[i] == 3:
      # Update risk levels by resetting Component-Value-at-Risk
      # All process to gather Component-Value-at-Risk and apply it to current prices
      cartera = pd.read_excel(csv.Path.values[i])
      previous = cartera.copy()
      path = str(clients['Path'][i])
      portfolio = pd.DataFrame(index=cartera.iloc[:,0]) 
      info = data.copy()
      update = pd.DataFrame(info[f'{portfolio.index[0]}'].values,columns=[f'{portfolio.index.values[0]}'],index=info.index)
      for j in range(1, len(portfolio)):
          update[f'{portfolio.index.values[j]}'] = info[f'{portfolio.index[j]}'].values
      returns = update.pct_change()
      correlation = returns.corr() # correlation
      covariance = returns.cov()  # covariance
      instruments = pd.DataFrame(index= update.columns)
      sample = np.random.random_sample(size=(len(update.columns),1)) + (1.0 / len(data.columns))
      sample /= np.sum(sample)
      instruments['weights'] = sample # secure allocation is equal 1
      instruments['deltas'] = (instruments.weights * correlation).sum() # deltas as elasticity of the assets
      instruments['Stdev'] = returns.std()
      instruments['stress'] = (instruments.deltas * instruments.Stdev) * 3 # stress applied at 4 deviations
      instruments['portfolio_stress'] = instruments.stress.sum() # the stress of the portfolio
      risk = pd.DataFrame(index=update.columns)
      risk['numerator'] = (instruments.deltas.multiply(covariance)).sum()
      risk['denominator'] = update.pct_change().std() * (-2.365)
      risk['GradVaR'] = -risk.numerator / risk.denominator
      risk['CVaRj'] = risk.GradVaR * instruments.deltas # Component VaR of the Risk Factors j
      risk['thetai'] = (risk.CVaRj * correlation).sum() # Theta i of the instruments
      risk['CVaRi'] = risk.thetai * (1/len(update.columns)) # Component VaR of the Instruments i
      risk['totalCVaRi'] = risk.CVaRi.sum() #total CVaR of the portfolio
      risk['CVaRattribution'] = risk.CVaRi / risk.totalCVaRi # risk allocation by instrument in the portfolio
      riskadj = pd.DataFrame(index=update.columns)
      riskadj['base'] = instruments['weights'].values
      riskadj['CVaRattribution'] = risk.CVaRattribution.sort_values(axis=0,ascending=False)
      riskadj['new'] = cartera['weights'].values  # Choosing the option with the highest return
      riskadj['condition'] = (riskadj.base / riskadj.CVaRattribution)
      riskadj['newrisk'] = (riskadj.new / riskadj.CVaRattribution)
      riskadj['differences'] = (riskadj.newrisk - riskadj.condition)  # apply this result as a percentage to multiply new weights
      riskadj['adjustments'] = (riskadj.newrisk - riskadj.condition) / riskadj.condition #ALARM if its negative sum up the difference, 
                                                  #if it is positive rest it, you need to have 0
      riskadj['suggested'] = riskadj.new * (1 + riskadj.adjustments)   
      riskadj['tototal'] = riskadj.suggested.sum()
      riskadj['MinCVaR'] = riskadj.suggested / riskadj.tototal
      riskadj[riskadj.MinCVaR>= 0.12] = 0.12
      riskadj['MinCVaR'] = riskadj['MinCVaR'] / sum(riskadj['MinCVaR'])
      portfolio = pd.DataFrame(index=cartera.iloc[:,0]) # rewrite
      portfolio['nominal'] = cartera['nominal'].values
      portfolio['pricePaid'] = cartera['price'].values
      portfolio['weights'] = riskadj.MinCVaR.values 
      portfolio['notionalStart'] = sum(portfolio['nominal'] * portfolio['pricePaid'])
      portfolio['oldLiquidity'] = cartera['liquid'].values
      portfolio['priceToday'] = update.tail(1).T.values
      portfolio['notionalToday'] = sum(portfolio['priceToday'] * portfolio['nominal'])
      portfolio['PnLpercent'] = portfolio['notionalToday'] / portfolio['notionalStart']
      portfolio['PnLpercentEach'] = portfolio['priceToday'] / portfolio['pricePaid']
      portfolio['nominalNew'] = ((portfolio['weights'] * (portfolio['notionalToday'] + portfolio['oldLiquidity'])) // portfolio['priceToday']) # nuevo nominal
      portfolio['adjust'] = portfolio['nominalNew'] - portfolio['nominal'] # ajuste nominal
      portfolio['percentReb'] = (portfolio['nominalNew'] * portfolio['priceToday']) / sum(portfolio['nominalNew'] * portfolio['priceToday'])
      # Columnas vinculantes para conectar mes anterior con el proximo ya armado
      portfolio['notionalRebalance'] = sum(portfolio['nominalNew'] * portfolio['priceToday'])
      portfolio['liquidityToReinvest'] =  (portfolio['notionalToday'] + portfolio['oldLiquidity']) - portfolio['notionalRebalance']
      capital = int(portfolio.notionalToday.values[0] + portfolio.liquidityToReinvest.values[0])
      basics = portfolio.copy()
      basics = tracker.BacktoBasics(basics)
      folder = os.makedirs('Oldportfolios',exist_ok=True)
      name = path
      old = name.replace('./DATABASE/','./Oldportfolios/')
      shutil.move(f'{name}',f'{old}')
      newName = ' '.join(path.split()[:-1])
      newName = (path.split()[:-1])
      newName[-2] = str(capital)
      newName = ' '.join(newName) + ' ' + str(dt.date.today()) + '.xlsx'
      writer = pd.ExcelWriter(f'{newName}',engine='xlsxwriter')
      basics.to_excel(writer,sheet_name=f"Risk {dt.date.today()}")
      portfolio.to_excel(writer,sheet_name='Risk Updated')
      previous.to_excel(writer,sheet_name='Previous Composition')
      writer.save()
      clients.TimeStamp.values[i] = dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
      # Reset Status to 0 as there any changes pending to do
      clients.Status.values[i] = 0
      clients.Change.values[i] = 0


# Remove unnecessary & repeated columns 
to_delete = list(filter(lambda i: (i[0:3] == 'Unn'),clients.columns.to_list()))

for i in range(len(to_delete)):
    if to_delete[i] in clients.columns.to_list():
        del clients[f'{to_delete[i]}']


clients.to_csv('scanner.csv',index=False)
