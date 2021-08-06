import smtplib    
from contextlib import contextmanager
import pandas as pd, datetime as dt,numpy as np
import re, os, ssl
import credentials, glob 
import base64
from templateReport import * # template html of all content of the email
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email import encoders

today = dt.date.today().strftime('%Y-%m-%d')
hoy = dt.date.today().strftime('%d/%m/%y')
excel = pd.read_csv(f'/home/lorenzo/Quanvas/Dollar Futures {today}.csv')
excel = excel.rename(columns={'Unnamed: 0':''})
excel['Close'] = ['$ {:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((excel['Close'].astype(float)).values)]
excel['30 days'] = ['$ {:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((excel['30 days'].astype(float)).values[:-2])] + [np.nan,np.nan]
excel['Percent'] = ['{:,.2f} %'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((excel['Percent'].astype(float)).values[:-2])] + [np.nan,np.nan]
excel.iloc[:,-4:] = excel.iloc[:,-4:] * 100.0
excel['Impl. Rate'] = [np.nan] + ['{:,.2f} %'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((excel['Impl. Rate'].astype(float)).values[1:])]
excel['Previous Impl. Rate'] = [np.nan] + ['{:,.2f} %'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((excel['Previous Impl. Rate'].astype(float)).values[1:-2])] + [np.nan,np.nan]
excel['Effective Annual Rate'] = [np.nan] + ['{:,.2f} %'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((excel['Effective Annual Rate'].astype(float)).values[1:])]
excel['Impl. Rate 30d'] = [np.nan] + ['{:,.2f} %'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((excel['Impl. Rate 30d'].astype(float)).values[1:])]

html_file = excel.to_html(na_rep = "",index=False).replace('<th>','<th  style="color:white">').replace('<table>','<table style="width:100%">')


# Stats to show
exchanges = pd.read_csv('/home/lorenzo/Quanvas/Exchanges.csv')
exchanges.index = exchanges.iloc[:,0].values
del exchanges['Date']
# Last Price
mep,adr,dollar = exchanges.iloc[-1,0],exchanges.iloc[-1,1],exchanges.iloc[-1,2]
# Price 3 months before
mep3,adr3,dollar3 = exchanges.iloc[-60,0],exchanges.iloc[-60,1],exchanges.iloc[-60,2]
# Return over 3 months time lapse
mep3R, adr3R, dollar3R = exchanges.iloc[-60:,0].pct_change().sum(),exchanges.iloc[-60:,1].pct_change().sum(),exchanges.iloc[-60:,2].pct_change().sum()

# We assume that the image file is in the same directory that you run your Python script from
fp = open('/home/lorenzo/Quanvas/Exchanges.png', 'rb')
image1 = MIMEImage(fp.read())
fp.close()
fp = open('/home/lorenzo/Quanvas/SpotnFutures.png', 'rb')
image2 = MIMEImage(fp.read())
fp.close()
fp = open('/home/lorenzo/Quanvas/futuresReturn.png', 'rb')
image3 = MIMEImage(fp.read())
fp.close()

# send especific email
server = smtplib.SMTP('smtp.gmail.com', 587)
server.ehlo()
server.starttls()
# login account + password
server.login(credentials.account,credentials.password)

clients = pd.read_csv('/home/lorenzo/Quanvas/scanner.csv')
hoy = dt.date.today().strftime('%d-%m-%Y')
destinatarios = ['lreyes@udesa.edu.ar']#, f'{clients.Email.values[i]}']

def sendEmails(message):
    msg = MIMEMultipart('alternative',text='URGENT!')
    msg['X-Priority'] = '1'
    msg['Subject'] = f"Quanvas Estado Cambiario Argentino {clients.Name[i]} {hoy}"
    msg['From'] = credentials.account
    msg['To'] = ",".join(destinatarios) 
    # body of the email
    part1 = message
    #part1 = _fix_eols(part1).encode('utf-8')
    part1 = MIMEText(part1, 'html')
    msg.attach(part1)
    ## Specify the  ID according to the img src in the HTML part
    image1.add_header('Content-ID', '<Exchanges>')
    msg.attach(image1)
    image2.add_header('Content-ID', '<SpotnFutures>')
    msg.attach(image2)
    image3.add_header('Content-ID', '<futuresReturn>')
    msg.attach(image3)
    server.sendmail(credentials.account,
                    destinatarios,
                    msg.as_string())
    

for i in range(len(clients)):    
  morning = f'<h2>Buenos dias {clients.Name.values[i]}</h2>'
  plotForex = f"""<img src="cid:Exchanges" style="width:80%; display: block; margin-left: auto; margin-right: auto;" loading="lazy">"""  

  preview = """<h2>El Estado del mercado cambiario argentino se describe bajo los siguientes indicadores.</h2>"""
  dolares = f"""<h3><ul>
                    <li>Cambio Dolar MEP:  {round(mep3R*100.0,2)}%    [MEP HOY    ${round(mep,2)}, 3 Meses Antes ${round(mep3,2)}].</li>
                    <li>Cambio Dolar ADR:  {round(adr3R*100.0,2)}%    [ADR HOY    ${round(adr,2)}, 3 Meses Antes ${round(adr3,2)}].</li>
                    <li>Cambio Dolar País: {round(dollar3R*100.0,2)}% [Dolar HOY$ ${round(dollar,2)}, 3 Meses Antes ${round(dollar3,2)}].</li>
                </ul></h3>"""

  derivatives = """<h3>Información Respecto a la Curva de Dolares Futuros MATBA-ROFEX.</h3>"""
  series = """<h3>Serie Spot y Futuros</h3>"""
  plotFutures = """<img src="cid:SpotnFutures" style="width:80%; display: block; margin-left:auto; margin-right:auto;" loading="lazy">"""
  retorno = """<h3>Retorno del Spot y Futuros</h3>"""
  plotReturn = """<img src="cid:futuresReturn" style="width:80%; display: block; margin-left:auto; margin-right:auto;" loading="lazy">"""

  firma = """<h2>Esperamos que esta minuta lo mantenga informado.</h2>
            <h2>Sin más saludamos, equipo QUANVAS.</h2> """



  message = style + highlight + morning + preview + dolares + plotForex + derivatives + html_file + series + plotFutures + retorno + plotReturn + firma + end_html 

  e = sendEmails(message)
  print(f"{dt.datetime.now().strftime('%H:%M:%S:%f')} Quanvas Report {clients.Name.values[i]} at {clients.Email.values[i]} SENT!!!")
  e

server.quit()
