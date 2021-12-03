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
from maintainer_report import * 

csv = pd.read_csv('/home/lorenzo/Quanvas/maintain.csv')
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
  name, action, capital, oldcapital, change = \
      csv.Name[i], csv.Action[i],int(csv.Capital[i]),int(csv.oldCapital[i]), csv.Change[i]
  withdraw = ''
  if action == 'Cambio':
    withdraw = int(csv.Withdraw[i])
    withdraw = '${:,.2f}'.format(withdraw).replace('.','p').replace(',','.').replace('p',',')

  portfolio = pd.DataFrame(index=cartera.iloc[:,0]) # rewrite
  portfolio = cartera.iloc[:,5:-2].copy()
  portfolio.index = cartera.iloc[:,0].to_list()
  portfolio['nominal'] = ['{:,.0f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['nominal'].astype(float)).values)]
  portfolio['invested'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['invested'].astype(float)).values)]
  portfolio['percentage'] = ['{:,.2f}%'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((portfolio['percentage'].astype(float)).values * 100.0)]
  change = '${:,.2f}'.format(change).replace('.','p').replace(',','.').replace('p',',')
  capital = '${:,.2f}'.format(capital).replace('.','p').replace(',','.').replace('p',',')
  oldcapital = '${:,.2f}'.format(oldcapital).replace('.','p').replace(',','.').replace('p',',')
  portfolio = portfolio.rename(columns={'nominal':'CANTIDAD','invested':'INVERTIDO','percentage':'PONDERACIÓN'})
  email = csv.Email[i]
  
  text = f"""<h1>Buenos dias {name}.</h1><br />"""
  optional = ''
  if withdraw != '':
    optional = ' Cambio de Capital por ' + f'{withdraw}'
  detalle = f"""<h3>Datos Inversión Cambiada:
                  <ul>
                    <li>Operación de {action}.{optional}</li>
                    <li>Monto de Inversión: {capital}. Anterior {oldcapital}</li>
                    <li>Cambio {change}</li>
                  </ul>
                </h3> """
              
  html_cerrado = portfolio.to_html(na_rep = "").replace('<table','<table id="effect" style="width:70%; height:auto;"').replace('<th>','<th style = "background-color: rgb(60,179,113); color:black">')


  advertencia = """<h3>Tras esta decisión debemos estar pendientes a:</h3><br /> 
            <p>La tendencia del mercado y a las necesidades para operar para el monitoreo diario de la inversión.</p>"""
  firma = '<h2>Se adjunta excel con detalle completo y con propuesta de rebalanceo</h2>'
  html_file = style + highlight + text + detalle + html_cerrado + advertencia + firma + end_html

  destinatarios = ['lreyes@udesa.edu.ar', f'{clients.Email.values[i]}']

  def sendEmail(html_file):
      msg = MIMEMultipart('alternative')
      msg['X-Priority'] = '1'
      msg['Subject'] = f"Actualización QUANVAS {name} {hoy}"
      msg['From'] = credentials.account
      msg['To'] = ",".join(destinatarios)
      # Large Excel 
      fp = open(f'{csv.Path.values[i]}', 'rb')
      parte = MIMEBase('application','vnd.ms-excel')
      parte.set_payload(fp.read())
      encoders.encode_base64(parte)
      parte.add_header('Content-Disposition', 'attachment', filename=f'Cuenta Actualizada {name}.xlsx')
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
      newname = f'{csv.NewName.values[i]}'
      os.rename(f'{csv.Path.values[i]}',f'{csv.NewName.values[i]}')
      todb = newname.replace('Maintenance','DATABASE')
      shutil.move(f'{newname}',f'{todb}')


  e = sendEmail(html_file)
  print(f"{dt.datetime.now().strftime('%H:%M:%S:%f')} UPDATE to {name} SENT!!!")
  e

server.quit()
