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
from scanner import *

hoy = dt.date.today().strftime('%d-%m-%Y')

clients = pd.read_csv('/home/lorenzo/Quanvas/scanner.csv')

for i in range(1): #(len(clients)):
    cliente = str(clients.Name.values[i])
    read_file = pd.read_excel('/home/lorenzo/Quanvas/' + str(clients.Path.values[i]).replace('./',''))
    read_file = tracker.PortfolioMonitor(read_file)
    read_file.to_csv(f'/home/lorenzo/Quanvas/{cliente} Update {hoy}.csv')
    read_file.index = read_file.index.to_list()    
    pnl = read_file.PnLpercent.values[0].copy()
    read_file['nominal'] = ['{:,.0f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((read_file['nominal'].astype(float)).values)]
    read_file['pricePaid'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((read_file['pricePaid'].astype(float)).values)]
    read_file['weights'] = ['{:,.2f}%'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((read_file['weights'].astype(float)).values * 100.0)]
    read_file['notionalStart'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((read_file['notionalStart'].astype(float)).values)]    
    read_file['oldLiquidity'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((read_file['oldLiquidity'].astype(float)).values)]
    read_file['priceToday'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((read_file['priceToday'].astype(float)).values)]
    read_file['notionalToday'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((read_file['notionalToday'].astype(float)).values)]    
    read_file['PnLpercent'], read_file['PnLpercentEach'] = read_file['PnLpercent'] - 1.0, read_file['PnLpercentEach'] - 1.0
    read_file['PnLpercent'] = ['{:,.2f}%'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((read_file['PnLpercent'].astype(float)).values * 100.0)]
    read_file['PnLpercentEach'] = ['{:,.2f}%'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((read_file['PnLpercentEach'].astype(float)).values * 100.0)]
    read_file['nominalNew'] = ['{:,.0f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((read_file['nominalNew'].astype(float)).values)]
    read_file['adjust'] = ['{:,.0f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((read_file['adjust'].astype(float)).values)]
    read_file['percentReb'] = ['{:,.2f}%'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((read_file['percentReb'].astype(float)).values * 100.0)]
    read_file['notionalRebalance'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((read_file['notionalRebalance'].astype(float)).values)]
    read_file['liquidityToReinvest'] = ['${:,.2f}'.format(i).replace('.','p').replace(',','.').replace('p',',') for i in list((read_file['liquidityToReinvest'].astype(float)).values)]

    text = f"""<h1>Resumen de cuenta {cliente} {hoy}.</h1><h3>Estado actual en composición y rendimiento.<br /></h3>"""
    detalle = f"""<h3>
              <ul>
                <li>Retorno Acumulado: {round((pnl * 100)-100,2)}%.</li>
                <li>Columna Adjust: sugerencia de cambios en la cartera para su actualización.</li>
                <li>Columna PnLpercent: retorno total de la cartera.</li>
                <li>Columna PnLpercentEach: retorno invididual de cada componente.</li>
              </ul></h3><br />"""
    html_cerrado = read_file.to_html(na_rep = "").replace('<table','<table id="effect" style="width:500px;"').replace('<th>','<th style = "background-color: rgb(60,179,113); color:black">')

    advertencia = """<h3>Factores a estar atentos:<br />
        <ul>
            <li>Tendencia del mercado. Ya sea por análisis técnico, fundamental o evento a esperar</li>
            <li>Necesidad de liquidez para terminar posiciones.</li>
        </ul></h3>"""
    firma = '<p>Esperamos que esta minuta lo mantenga informado.<br /></p><p>Sin más saludamos, equipo QUANVAS.</p>'

    html_file = style + highlight + text + detalle + html_cerrado + advertencia + firma + end_html

    destinatarios = ['lreyes@udesa.edu.ar', f'{clients.Email.values[i]}']

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
    os.remove(f'/home/lorenzo/Quanvas/{cliente} Update {hoy}.csv')
    print(f"{dt.datetime.now().strftime('%H:%M:%S:%f')} Portfolio to {cliente} SENT!!!")
    e
