import pandas as pd, datetime as dt
import smtplib, re, os 
import credentials, glob 
import base64, shutil
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email import encoders
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
  font-size: 10px;
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

rofex = pd.read_html('http://datacenter.matba.com.ar/ajustesdc.aspx')

tabla = rofex[16]
tabla = tabla.iloc[:,2:]
tabla.columns = tabla.iloc[0,:].values
tabla = tabla.iloc[3:,:]
tabla = tabla.drop(['Aper.', 'Bajo', 'Alto', 'Ult.','Vol.','Vol. IRC','Var/O.I.', 'Mon'],axis=1)
tabla = tabla.rename(columns={"PosiciÃ³n":"Futuro"})

destinatarios =  ['lorenzo.reyes@firstcma.com','hector.gagliardi@firstcfa.com']

for i in range(1):
    html_file = tabla.to_html(na_rep = "",index=False).replace('<table>','<table style="width:900px;">')
    text = f'<img src="cid:header" style="width:900px; height:200px"><br /><h3>Este reporte se enviará Lunes a Viernes a las 20:00.</h4><p>Cuadro Agro.<br /></p>'
    firma = '<p>Esperamos que esta información le sea de su utilidad.<br /></p><p>Saludos</p>'
    datos = """\
      <img src="cid:footer" style="width:900px; height:225px;">        
      """
    html_file = style + text + html_file + firma + datos + end_html

    def sendEmail(html_file):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Tabla Agro {fecha}"
        msg['From'] = credentials.account
        msg['To'] = ",".join(destinatarios)  # str(",".join(clientDict.Mails[i]))
        image.add_header('Content-ID', '<header>')
        msg.attach(image)
        image2.add_header('Content-ID', '<footer>')
        msg.attach(image2)
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



