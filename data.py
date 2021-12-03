import pandas as pd
import datapungi_imf as dpi
import wbdata
import matplotlib.pyplot as plt

data = dpi.data()

germanyreal = data.data('IFS/M.DE.EREER_IX?startPeriod=1993&endPeriod=2020')
polandreal = data.data('IFS/M.PL.EREER_IX?startPeriod=1993&endPeriod=2020')
ukrainereal = data.data('IFS/M.UA.EREER_IX?startPeriod=1993&endPeriod=2020')

ukrainenominal = data.data('IFS/M.UA.ENEE_XDC_EUR_RATE?startPeriod=1993&endPeriod=2020')
polandnominal = data.data('IFS/M.PL.ENEE_XDC_EUR_RATE?startPeriod=1993&endPeriod=2020')

pricegerman = data.data('IFS/M.DE.PCPI_IX?startPeriod=1993&endPeriod=2020')
pricepolish = data.data('IFS/M.PL.PCPI_IX?startPeriod=1993&endPeriod=2020')
priceukranian = data.data('IFS/M.UA.PCPI_IX?startPeriod=1993&endPeriod=2020')

realrates = pd.DataFrame(index=ukrainereal.index)
realrates['germany'] = germanyreal['value'].tail(len(ukrainereal))
realrates['poland'] = polandreal['value'].tail(len(ukrainereal))
realrates['ukraine'] = ukrainereal['value']
realrates = realrates.tail(330)

nominalrates = pd.DataFrame(index=ukrainenominal.index)
nominalrates['poland'] = polandnominal['value']
nominalrates['ukraine'] = ukrainenominal['value']

prices = pd.DataFrame(index=pricegerman.index)
prices['german'] = pricegerman['value']
prices['polish'] = pricepolish['value']
prices['ukranian'] = priceukranian['value'].fillna(method='ffill')

bilateral = pd.DataFrame(index=prices.index)
bilateral['Poland'] = (realrates['poland'] * prices['german']) / prices['polish']
bilateral['Ukraine'] = (realrates['ukraine'] * prices['german']) / prices['ukranian']


indicator = {'NY.GDP.MKTP.CD':'GDP'}
polandgdp = wbdata.get_dataframe(indicator, country="PL", convert_date=True)
ukrainegdp = wbdata.get_dataframe(indicator, country="UA", convert_date=True)
gdp = pd.DataFrame(index=polandgdp.index)
gdp['PolandGDP'] = polandgdp['GDP']
gdp['UkraineGDP'] = ukrainegdp['GDP']
gdp = gdp.dropna()

fig = plt.figure(figsize=(25,12))
ax1 = fig.add_subplot(211, ylabel='Real Exchange Adjusted')
bilateral.tail(280).plot(ax=ax1, lw=2., legend=True)
ax1.grid()
ax2 = fig.add_subplot(212, ylabel='Percentage Bilateral')
bilateral.tail(280).pct_change().cumsum().plot(ax=ax2, lw=2., legend=True)
ax2.grid()
plt.show()

writer = pd.ExcelWriter('PolandorUkraine.xlsx',engine='xlsxwriter')

realrates.to_excel(writer,sheet_name="realrates")

nominalrates.to_excel(writer,sheet_name="nominalrates")

prices.to_excel(writer, sheet_name="prices")

bilateral.to_excel(writer,sheet_name="bilateralexchange")

writer.save()