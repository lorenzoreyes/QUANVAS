import pandas as pd, datetime as dt, numpy as np
import smtplib, re, os, ssl 
import credentials, glob 
import base64, shutil
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email import encoders
import trackATM as tracker
from templateReport import * # template html of all content of the email
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

data = yahoo.download(lista,period="60d",interval="2m")["Adj Close"].fillna(method="ffill")
clients = pd.read_csv('/home/lorenzo/Quanvas/scanner.csv')
hoy = dt.date.today().strftime('%d-%m-%Y')

# iterate clients
# first grab the client & update data
# once updated, send the email
# First set the server
server = smtplib.SMTP('smtp.gmail.com', 587)
server.ehlo()
server.starttls()
# login account + password
server.login(credentials.account,credentials.password)


for i in range(len(clients)):
  clients.Path.values[i] = str(clients.Path.values[i]).replace('./','/home/lorenzo/Quanvas/')
  cartera = pd.read_excel(clients.Path.values[i])
  file_path, timestamp = str(clients.Path.values[i]), str(clients.Path.values[i]).split()[-1].split('.')[0]
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
  portfolio['liquidityToReinvest'] =  (portfolio['notionalToday'] + portfolio['oldLiquidity']) - portfolio['notionalRebalance']
  cliente = str(clients.Name.values[i])
  portfolio.to_csv(f'/home/lorenzo/Quanvas/{cliente} Update {hoy}.csv')
  portfolio.index = portfolio.index.to_list()  
  pnl = portfolio.PnLpercent.values[0].copy()
  portfolio = portfolio[portfolio.nominal!=0.0].dropna()
  portfolio['nominal'] = ['{:,.0f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['nominal'].astype(float)).values)]
  portfolio['pricePaid'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['pricePaid'].astype(float)).values)]
  portfolio['weights'] = ['{:,.2f}%'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['weights'].astype(float)).values * 100.0)]
  portfolio['notionalStart'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['notionalStart'].astype(float)).values)]    
  portfolio['oldLiquidity'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['oldLiquidity'].astype(float)).values)]
  portfolio['priceToday'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['priceToday'].astype(float)).values)]
  portfolio['notionalToday'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['notionalToday'].astype(float)).values)]    
  portfolio['PnLpercent'], portfolio['PnLpercentEach'] = portfolio['PnLpercent'] - 1.0, portfolio['PnLpercentEach'] - 1.0
  portfolio['PnLpercent'] = ['{:,.2f}%'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['PnLpercent'].astype(float)).values * 100.0)]
  portfolio['PnLpercentEach'] = ['{:,.2f}%'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['PnLpercentEach'].astype(float)).values * 100.0)]
  portfolio['nominalNew'] = ['{:,.0f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['nominalNew'].astype(float)).values)]
  portfolio['adjust'] = ['{:,.0f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['adjust'].astype(float)).values)]
  portfolio['percentReb'] = ['{:,.2f}%'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['percentReb'].astype(float)).values * 100.0)]
  portfolio['notionalRebalance'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['notionalRebalance'].astype(float)).values)]
  portfolio['liquidityToReinvest'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['liquidityToReinvest'].astype(float)).values)]
  oldNotional = portfolio.notionalStart.values[0]
  newNotional = portfolio.notionalToday.values[0]
  oldLiquidity = portfolio.oldLiquidity.values[0]
  portfolio = portfolio.drop(['notionalStart','notionalToday','oldLiquidity','PnLpercent','nominalNew',\
          'adjust','percentReb','notionalRebalance','liquidityToReinvest'],axis=1)
  portfolio = portfolio.rename(columns={'nominal':'CANTIDAD','pricePaid':'PRECIO DE COMPRA','weights':'PONDERACIÓN','priceToday':'PRECIO HOY','PnLpercentEach':'GANANCIA/PERDIDA'})


  text = f"""<h1>Resumen de cuenta {cliente} {hoy}.</h1><h3>Estado actual en composición y rendimiento simplificado.<br /></h3>"""
  detalle = f"""<h3>
              <ul>
                <li>Retorno Acumulado: {round((pnl * 100)-100,2)}%.</li>
                <li>Valor inversión hoy {newNotional} versus inicial {oldNotional}.</li>
                <li>Liquidez remanente para reinvertir: {oldLiquidity}.</li>
                <li>Fecha de última modificación: {timestamp}.</li>
              </ul></h3>
              <br />"""
  html_cerrado = portfolio.to_html(na_rep = "").replace('<table','<table id="effect" style="width:50%; height:auto;"').replace('<th>','<th style = "background-color: rgb(60,179,113); color:black">')

  advertencia = """
            <hr />
            <h3>ACCIONES A CONSIDERAR:<br/>
                <ul>
                    <li>Actualizar Cartera: al hacer rebalanceo.</li>
                    <li>Cambiar Monto invertido: por medio de extracción o deposito.</li>
                    <li>Resetear nivel de riesgo: en busca de un rebalanceo para minimizar el riesgo.</li>
                </ul></h3>"""
  advertencia += """<h3>Factores a estar atentos:<br /> 
            <p>Tendencia del mercado. Ya sea por análisis técnico, fundamental o evento a esperar.<br />Necesidad de liquidez para terminar posiciones.</p>
        </ul></h3>"""
  firma = '<p>Esperamos que esta minuta lo mantenga informado.<br /></p><p>Sin más saludamos, equipo QUANVAS.</p>'
  firma += '<h1>Se adjunta excel con detalle completo y con propuesta de rebalanceo</h1>'
  html_file = style + highlight + text + detalle + html_cerrado + advertencia + firma + end_html

  # In order to save the actual template we are sending
  if i == 0:
     e = open('template.html','w') 
     e.write(html_file)
     e.close()

  #destinatarios = ['lreyes@udesa.edu.ar']#, f'{clients.Email.values[i]}']
  destinatarios = [f'{clients.Email.values[i]}']

  def sendEmail(html_file):
      msg = MIMEMultipart('alternative')
      msg['X-Priority'] = '1'
      msg['Subject'] = f"QUANVAS Resumen de Cuenta {cliente} {hoy}"
      msg['From'] = credentials.account
      msg['To'] = ",".join(destinatarios)
      # Large Excel 
      fp = open(f'/home/lorenzo/Quanvas/{cliente} Update {hoy}.csv', 'rb')
      parte = MIMEBase('application','vnd.ms-excel')
      parte.set_payload(fp.read())
      encoders.encode_base64(parte)
      parte.add_header('Content-Disposition', 'attachment', filename=f'Resumen Cuenta {cliente}.csv')
      msg.attach(parte)
      part1 = html_file
      part1 = MIMEText(part1, 'html')
      msg.attach(part1)
      part1 = html_file
      part1 = MIMEText(part1, 'html')
      msg.attach(part1)
      server.sendmail(credentials.account,
                    destinatarios,
                    msg.as_string())


  e = sendEmail(html_file)
  os.remove(f'/home/lorenzo/Quanvas/{cliente} Update {hoy}.csv')
  print(f"{dt.datetime.now().strftime('%H:%M:%S:%f')} Portfolio to {cliente} {file_path} SENT!!!")
  e

server.quit()
