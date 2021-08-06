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
from scanner import *
import yfinance as yahoo 

file = []

for filename in glob.iglob('/home/lorenzo/Quanvas/NewOnes/*'):
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

csv['Symbol'] = [i.split()[0][2:] for i in csv.Path.to_list()]
csv['Name'] = [' '.join(i.split()[1:3]) for i in csv.Path.to_list()]
csv['Email'] = [(i.split()[3]) for i in csv.Path.to_list()]
csv['Capital'] = [i.split()[4] for i in csv.Path.to_list()]
csv['Optimization'] = [i.split()[5] for i in csv.Path.to_list()]
csv['Status'] = 0
csv['Change'] = 0
csv['TimeStamp'] = dt.datetime.today().strftime('%H:%M:%S %d-%m-%Y')
csv.index = range(len(csv))

csv.to_csv('NewOnes.csv',index=False)

clients = csv

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


for i in range(len(file)):
  cartera = pd.read_excel(csv.Path.values[i])
  portfolio = pd.DataFrame(index=cartera.iloc[:,0]) # rewrite
  portfolio = cartera.iloc[:,5:-2].copy()
  portfolio.index = cartera.iloc[:,0].to_list()
  capital, investment, liquidity, risk = cartera.capital[0].copy(), cartera.total[0].copy(),cartera.liquid[0].copy(),csv.Path[0].split()[-2]
  portfolio['nominal'] = ['{:,.0f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['nominal'].astype(float)).values)]
  portfolio['invested'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['invested'].astype(float)).values)]
  portfolio['percentage'] = ['{:,.2f}%'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['percentage'].astype(float)).values * 100.0)]
  investment = '${:,.2f}'.format(investment).replace('.','p').replace(',','.').replace('p',',')
  capital = '${:,.2f}'.format(capital).replace('.','p').replace(',','.').replace('p',',')
  liquidity = '${:,.2f}'.format(liquidity).replace('.','p').replace(',','.').replace('p',',')
  
  portfolio = portfolio.rename(columns={'nominal':'CANTIDAD','invested':'INVERTIDO','percentage':'PONDERACIÓN'})
  cliente = csv.Path[i].split()[1] + ' ' + csv.Path[i].split()[2]
  email = csv.Path[i].split()[3]
  
  text = f"""<h1>Bienvenido {cliente} a QUANVAS.</h1><br /><h3>A la fecha de {hoy} se ha creado la siguiente recomendación en base al mercado que desea operar y acorde a su perfil de riesgo.<br /></h3>"""
  detalle = f"""<h3>Datos de su cartera:
              <ul>
                <li>Monto de Inversión: {capital}.</li>
                <li>Perfil de Riesgo: {risk}.</li>
                <li>Riesgos de 1 a 4 de Conservador a más Agresivo (MinVar, Sharpe, Sortino, SharpeUnbound).</li>
                <li>INVERTIDO: {investment}.</li>
                <li>Liquidez remanente para reinvertir: {liquidity}.</li>
              </ul></h3> """
              
  html_cerrado = portfolio.to_html(na_rep = "").replace('<table','<table id="effect" style="width:70%; height:auto;"').replace('<th>','<th style = "background-color: rgb(60,179,113); color:black">')

  advertencia = """<h3>ACCIONES A CONSIDERAR:<br/>
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

  destinatarios = ['lreyes@udesa.edu.ar', f'{clients.Email.values[i]}']

  def sendEmail(html_file):
      msg = MIMEMultipart('alternative')
      msg['X-Priority'] = '1'
      msg['Subject'] = f"Bienvenido a QUANVAS {cliente} {hoy}"
      msg['From'] = credentials.account
      msg['To'] = ",".join(destinatarios)
      # Large Excel 
      fp = open(f'{csv.Path.values[i]}', 'rb')
      parte = MIMEBase('application','vnd.ms-excel')
      parte.set_payload(fp.read())
      encoders.encode_base64(parte)
      parte.add_header('Content-Disposition', 'attachment', filename=f'Resumen Cuenta {cliente}.xlsx')
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
      name = f'{csv.Path.values[i]}'
      todb = name.replace('NewOnes','DATABASE')
      shutil.move(f'{name}',f'{todb}')


  e = sendEmail(html_file)
  print(f"{dt.datetime.now().strftime('%H:%M:%S:%f')} Portfolio to {cliente} SENT!!!")
  e

server.quit()
