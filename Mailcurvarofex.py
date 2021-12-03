import pandas as pd, datetime as dt
import smtplib, re, os 
import credentials, glob 
import base64, shutil
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email import encoders
from CurvaRofex import *

fecha = hoy = dt.date.today().strftime('%d-%m-%Y')

style = '''\
<!DOCTYPE html>
<html>
<head>
<style>
h1, h2, h3, h5, p {
  font-family: 'Trebuchet MS', sans-serif;
}
h1 {  
  text-align: center;
}
table, td, th {
  font-family: 'Trebuchet MS', sans-serif;
  font-size: 12px;
  border: 1px solid black;
  padding: 1px 1px 1px 1px;
  white-space: nowrap;
  text-align: center;
  border-collapse: collapse;
}
th {
  height: 20 px;
  color: white;
  background-color: rgb(0, 0, 78);
}
table {
  table-layout: auto;
  width: 900px;
}

</style>
</head>
<body>'''
end_html =''' 
</body>
</html>'''


fp = open('/home/lorenzo/Desktop/Akira/Chartboard/header.png', 'rb')
image = MIMEImage(fp.read())
fp.close()
fp = open('/home/lorenzo/Desktop/Akira/Chartboard/footer.png', 'rb')
image2 = MIMEImage(fp.read())
fp.close()
fp = open('/home/lorenzo/Desktop/Akira/Chartboard/curvadolar.png', 'rb')
image3 = MIMEImage(fp.read())
fp.close()

#fp = open('/home/lorenzo/Desktop/Akira/Chartboard/tnaTri.png', 'rb')
#image4 = MIMEImage(fp.read())
#fp.close()
#fp = open('/home/lorenzo/Desktop/Akira/Chartboard/ajusteFuturos.png', 'rb')
#image5 = MIMEImage(fp.read())
#fp.close()
#fp = open('/home/lorenzo/Desktop/Akira/Chartboard/LiquidezF.png', 'rb')
#image6 = MIMEImage(fp.read())
#fp.close()


destinatarios =  ['lreyes@udesa.edu.ar']


for i in range(1):
    read_file = pd.read_csv(f'/home/lorenzo/Desktop/Akira/Chartboard/Curva/CurvaRofex {hoy}.csv')
    read_file['Variación%'] = [''] + ['{:,.2f}%'.format(i) for i in list(read_file.iloc[1:,4].values)]
    read_file.iloc[:,1] = ['{:,.2f}'.format(i) for i in read_file.iloc[:,1].to_list()]
    read_file.iloc[:,2] = ['{:,.2f}'.format(i) for i in read_file.iloc[:,2].to_list()]
    read_file['Volumen'] = [''] +['{:,.0f}'.format(i) for i in list(read_file.iloc[1:,5].values)]
    read_file['Interés Abierto'] = [''] + ['{:,}'.format(i).replace(',','.') for i in list(read_file.iloc[1:,7].values)]
    read_file['TNA'] = [''] + ['{:,}%'.format(i) for i in list(read_file.iloc[1:,-4].values)]
    read_file['TNA Ant'] = [''] + ['{:,}%'.format(i) for i in list(read_file.iloc[1:,-2].values)]
    read_file['TEA'] = [''] + ['{:,}%'.format(i) for i in list(read_file.iloc[1:,-2].values)]
    read_file['TNA 30d'] = [''] + ['{:,}%'.format(i) for i in list(read_file.iloc[1:,-1].values)]
    read_file['Total Volumen'] = [''] + ['{:,.2f}%'.format(i) for i in list(read_file.iloc[1:,6].values * 100)]
    read_file['Total Int. Ab.'] = [''] + ['{:,.2f}%'.format(i) for i in list(read_file.iloc[1:,8].values * 100)]
    read_file['dias'] = [''] + ['{:,.0f}'.format(i) for i in list(read_file.iloc[1:,9].values)]


    html_file = read_file.to_html(na_rep = "",index=False).replace('<table>','<table style="width:900px;">')
    text = f'<img src="cid:header" style="width:900px; height:200px"><br /><h3>Este reporte se enviará Lunes a Viernes.</h4><p>Cuadro Curvas Tasas de Interés de Rofex al dia de la fecha.<br /></p>'
    grafico = '<img src="cid:curvadolar" style="width:800px; height:300px;">'
    firma = '<p>Esperamos que esta información le sea de su utilidad.<br /></p><p>Saludos</p>'
    calculos = """<p>Cálculos:</p>
              <ul>
                <li>TNA o Tasa Implícita del plazo: (Futuro / Spot) - 1.0 *  (365 / días restantes)</li>
                <li>TNA Anterior: dato de la rueda previ  a.</li>
                <li>TEA o Tasa Efectiva Anual: (1 + (tasa TNA X (días restantes / 365) ^ (365 / días restantes) - 1</li>
                <li>TNA 30d o Tasa Mensual: ((1 + tasa TEA) ^ (1/12)) - 1</li>
              </ul>  
     """
    #grafico2 = '<img src="cid:tnaTri" style="width:800px; height:300px;">'
    #grafico3 = '<img src="cid:ajusteFuturos" style="width:800px; height:300px;">'
    #grafico4 = '<img src="cid:LiquidezF" style="width:800px; height:300px;">'

    datos = """\
      <img src="cid:footer" style="width:900px; height:225px;">        
      """
    #html_file = style + text + html_file + grafico + grafico2 + grafico3 + grafico4 + firma + calculos + datos + end_html
    html_file = style + text + html_file + grafico + firma + calculos + datos + end_html

    def sendEmail(html_file):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Informe Curva Rofex dia {fecha}"
        msg['From'] = credentials.account
        msg['To'] = ",".join(destinatarios)  # str(",".join(clientDict.Mails[i]))
        image.add_header('Content-ID', '<header>')
        msg.attach(image)
        image2.add_header('Content-ID', '<footer>')
        msg.attach(image2)
        image3.add_header('Content-ID', '<curvadolar>')
        msg.attach(image3)
        # Additional Charts
        #image4.add_header('Content-ID', '<tnaTri>')
        #msg.attach(image4)
        #image5.add_header('Content-ID', '<ajusteFuturos>')
        #msg.attach(image5)
        #image6.add_header('Content-ID', '<LiquidezF>')
        #msg.attach(image6)
        fp = open(f'/home/lorenzo/Desktop/Akira/Chartboard/Curva/CurvaRofex {hoy}.csv', 'rb')
        part = MIMEBase('application','vnd.ms-excel')
        part.set_payload(fp.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename=f'Informe Curva Rofex dia {fecha}.csv')
        msg.attach(part)
        # Large Excel Quarter
        #fp = open(f'/home/lorenzo/Desktop/Akira/Chartboard/FuturosRofex21.xlsx', 'rb')
        #parte = MIMEBase('application','vnd.ms-excel')
        #parte.set_payload(fp.read())
        #encoders.encode_base64(parte)
        #parte.add_header('Content-Disposition', 'attachment', filename='FuturosRofex.xlsx')
        #msg.attach(parte)
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
    e
