import pandas as pd, datetime as dt, numpy as np
import smtplib, re, os 
import credentials, glob 
import base64, shutil
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email import encoders
from templateReport import * # template html of all content of the email

hoy = dt.date.today().strftime('%d-%m-%Y')

clients = pd.read_csv('scanner.csv')

for i in range(1,len(clients)):
    cliente = str(clients.Names.values[i])
    read_file = pd.read_excel(clients.Path.values[i])
    read_file = read_file.rename(columns={'Unnamed: 0':'stocks'})
    read_file['capital'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((read_file['capital'].astype(float)).values)]
    read_file['price'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((read_file['price'].astype(float)).values)]
    read_file['weights'] = ['{:,.2f}%'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((read_file['weights'].astype(float)).values * 100.0)]
    read_file['cash'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((read_file['cash'].astype(float)).values)]    
    read_file['invested'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((read_file['invested'].astype(float)).values)]
    read_file['percentage'] = ['{:,.2f}%'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((read_file['percentage'].astype(float)).values * 100.0)]
    read_file['total'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((read_file['total'].astype(float)).values)]
    read_file['liquid'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((read_file['liquid'].astype(float)).values)]

    text = """<h1>Automatic Portfolios to invest.</h1><h3>This recommendation cover the scope of 4 different risk levels to face.<br /></h3>"""
    detalle = """<h3>
              <ul>
                <li>Minimal Variance Portfolio: Conservative profile. The idea is to have a solid investment in moments of high uncertainty.</li>
                <li>Sharpe Ratio Portfolio: it seeks to outperform the market using the sharpe ratio metric.</li>
                <li>Sortino Ratio Portfolio: the difference with previous metric is that sortino only focus on negative volatility, to minimize losses.</li>
                <li>Sharpe Unbound Portfolio: as the name suggests its the most volatile option. Sharpe Ratio without a focus to diversify</li>
              </ul></h3><br />
              <h3>Composition of recommended investment.</h3><br />"""
    html_cerrado = read_file.to_html(na_rep = "",index=False).replace('<table','<table id="effect" style="width:600px;"').replace('<th>','<th style = "background-color: black; color:white">')

    costos = """<h3>The service comprehends assesment and monitoring in the life cyle of the invesment.<br />
        <ul>
            <li>Fee for hiring the service.</li>
            <li>Monthly fee: 5% of perceived gains.</li>
        </ul></h3>"""
    firma = '<p>We hope this information had been useful.<br /></p><p>Kind Regards, QUANVAS team.</p>'

    html_file = style + highlight + text + detalle + html_cerrado + costos + firma + end_html

    destinatarios = ['lreyes@udesa.edu.ar'] + [clients.Emails.values[i]]

    def sendEmail(html_file):
        msg = MIMEMultipart('alternative')
        msg['X-Priority'] = '1'
        msg['Subject'] = f"QUANVAS Portfolio {cliente} {hoy}"
        msg['From'] = credentials.account
        msg['To'] = ",".join(destinatarios)
        # Large Excel 
        fp = open(f'/home/lorenzo/Quanvas/{clients.Path.values[i]}', 'rb')
        parte = MIMEBase('application','vnd.ms-excel')
        parte.set_payload(fp.read())
        encoders.encode_base64(parte)
        parte.add_header('Content-Disposition', 'attachment', filename=f'Recomendación {cliente}.xlsx')
        msg.attach(parte)
        part1 = html_file
        part1 = MIMEText(part1, 'html')
        msg.attach(part1)
        part1 = html_file
        part1 = MIMEText(part1, 'html')
        msg.attach(part1)
        s = smtplib.SMTP("smtp.gmail.com")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        # login account + password
        server.login(credentials.account,credentials.password)
        server.sendmail(credentials.account,
                    destinatarios,
                    msg.as_string())
        s.quit()

    e = sendEmail(html_file)
    print(f"{dt.datetime.now().strftime('%H:%M:%S:%f')} Portfolio to {cliente} SENT!!!")
    e
